#!/usr/bin/python3

import mysql.connector, pika, minio
import os, shutil, threading, time
from datetime import datetime
import utils, config


DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ["DB_PORT"])
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_NAME = os.environ["DB_NAME"]
MINIO_HOST = os.environ["MINIO_HOST"]
MINIO_PORT = os.environ["MINIO_PORT"]
MINIO_ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]
MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]
MINIO_BUCKET = os.environ["MINIO_BUCKET"]
MQ_HOST = os.environ["MQ_HOST"]
MQ_PORT = int(os.environ["MQ_PORT"])
MQ_USER = os.environ["MQ_USER"]
MQ_PASS = os.environ["MQ_PASS"]
MQ_QUEUE = os.environ["MQ_QUEUE"]


def init_dirs():
    os.makedirs(config.working_dir, exist_ok=True)
    os.makedirs(config.code_dir, exist_ok=True)
    os.makedirs(config.testcases_dir, exist_ok=True)
    os.makedirs(config.tester_dir, exist_ok=True)
    os.makedirs(config.program_out_dir, exist_ok=True)


def clean_up():
    shutil.rmtree(config.program_out_dir, ignore_errors=True)
    shutil.rmtree(config.tester_dir, ignore_errors=True)
    shutil.rmtree(config.testcases_dir, ignore_errors=True)
    shutil.rmtree(config.code_dir, ignore_errors=True)
    shutil.rmtree(config.working_dir, ignore_errors=True)
    init_dirs()


def init_db():
    db_connection =  mysql.connector.connect(host=DB_HOST, port=DB_PORT, 
                                             user=DB_USER, password=DB_PASS, 
                                             database=DB_NAME)
    return db_connection


def init_mq():
    mq_credentials = pika.PlainCredentials(username=MQ_USER, password=MQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_HOST, 
                                                                   port=MQ_PORT, 
                                                                   credentials=mq_credentials))
    channel = connection.channel()
    channel.queue_declare(queue=MQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    consumer_tag = channel.basic_consume(queue=MQ_QUEUE, on_message_callback=task_callback)
    return channel, consumer_tag


def init_minio():
    client = minio.Minio(endpoint=f"{MINIO_HOST}:{MINIO_PORT}", 
                         access_key=MINIO_ACCESS_KEY, 
                         secret_key=MINIO_SECRET_KEY,
                         secure=False,
                         )
    return client


db_connection = None
minio_client = None
processing = False
submission_ID = None
submission_table = None
delivery_tag = None
mutex = threading.Lock()

def task_callback(ch, method, properties, body):
    # Message: SubmissionPath SubmissionLanguage TimeLimit MemoryLimit TestcasesPath TesterPath SubmissionTable SubmissionID
    global processing, submission_ID, submission_table, delivery_tag
    try:
        # Message Decode
        mutex.acquire()
        try:
            processing = True
            successful_operation = False
            delivery_tag = method.delivery_tag
            body_split = body.decode('utf-8').split("\0")
            submission_table = body_split[6]
            submission_ID = body_split[7]
        finally:
            mutex.release()

        submission_path = body_split[0]
        submission_language = body_split[1]
        timelimit = body_split[2]
        memorylimit = body_split[3]
        testcases_path = body_split[4]
        tester_path = body_split[5]
        
        print(f"Received: [ Submission Path: {submission_path} - Submission Language: {submission_language} - Time Limit: {timelimit} - ", end="")
        print(f"Memory Limit: {memorylimit} - Testcases Path: {testcases_path} - Tester Path: {tester_path} - Submission Table: {submission_table} - ", end="")
        print(f"Submission ID: {submission_ID} ]")

        # Preparation
        submission_file = os.path.basename(submission_path)
        submission_dir = os.path.dirname(submission_path)
        minio_client.fget_object(MINIO_BUCKET, submission_path, config.code_dir + "/" + submission_file)
        testcases_file = os.path.basename(testcases_path)
        minio_client.fget_object(MINIO_BUCKET, testcases_path, config.testcases_dir + "/" + testcases_file)
        os.system(f"unzip -qq -o -d {config.testcases_dir} {config.testcases_dir}/{testcases_file} >/dev/null 2>&1")
        if tester_path == "" or tester_path == "Default":
            shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/default_tester/default_tester.py", config.tester_dir)
            tester_file = "default_tester.py"
        else:
            tester_file = os.path.basename(tester_path)
            minio_client.fget_object(MINIO_BUCKET, tester_path, config.tester_dir + "/" + tester_file)
        log_file = open(config.log_file, "w")
        log_file.write("-> Starting At: " + datetime.now().strftime("\%Y, %m, %d - %H:%M:%S") + "\n")
        log_file.close()

        # Start of Operation
        db_cursor = db_connection.cursor()

        # Compiling
        sql = f"UPDATE {submission_table} SET status = %s WHERE id = %s"
        val = ("Compiling", submission_ID)
        db_cursor.execute(sql, val)
        db_connection.commit()

        compile_successful = utils.compile(submission_file, submission_language)

        if compile_successful:
            # Testing
            sql = f"UPDATE {submission_table} SET status = %s WHERE id = %s"
            val = ("Testing", submission_ID)
            db_cursor.execute(sql, val)
            db_connection.commit()

            score = utils.run_testcases(submission_file, submission_language, timelimit, memorylimit, tester_file)
            log_path = submission_dir + "/log.txt"
            minio_client.fput_object(MINIO_BUCKET, log_path, config.log_file)
            results_path = submission_dir + "/results.txt"
            minio_client.fput_object(MINIO_BUCKET, results_path, config.results_file)
            sql = f"UPDATE {submission_table} SET status = %s, score = %s, results_path = %s, log_path = %s WHERE id = %s"
            val = ("Test Complete", str(score), results_path, log_path, submission_ID)
            db_cursor.execute(sql, val)
            db_connection.commit()
        else:
            log_path = submission_dir + "/log.txt"
            minio_client.fput_object(MINIO_BUCKET, log_path, config.log_file)
            sql = f"UPDATE {submission_table} SET status = %s, score = %s, results_path = '', log_path = %s WHERE id = %s"
            val = ("Compile Error", '0', log_path, submission_ID)
            db_cursor.execute(sql, val)
            db_connection.commit()

        successful_operation = True
    except Exception as e:
        print(e)
        log_path = submission_dir + "/log.txt"
        minio_client.fput_object(MINIO_BUCKET, log_path, config.log_file)
        sql = f"UPDATE {submission_table} SET status = %s, results_path = '', log_path = %s WHERE id = %s"
        val = ("Internal Error", log_path, submission_ID)
        db_cursor.execute(sql, val)
        db_connection.commit()


    clean_up()

    mutex.acquire()
    try:
        processing = False
        delivery_tag = None
        submission_table = None
        submission_ID = None
        if successful_operation == True:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        elif successful_operation == False:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        successful_operation = None
    finally:
        mutex.release()


def main():
    init_dirs()
    global db_connection, minio_client, processing, submission_ID, submission_table, delivery_tag
    db_connection = init_db()
    mq_channel, mq_consumer_tag = init_mq()
    minio_client = init_minio()

    try:
        mq_channel.start_consuming()
    except:
        mq_channel.basic_cancel(mq_consumer_tag)
        time.sleep(5)
        try:
            if processing == True:
                mq_channel.basic_nack(delivery_tag)
                db_cursor = db_connection.cursor()
                sql = f"UPDATE {submission_table} SET status = %s, results_path = '', log_path = '' WHERE id = %s"
                val = ("In Queue", submission_ID)
                db_cursor.execute(sql, val)
                db_connection.commit()
        finally:
            mutex.release()
            mq_channel.close()
            db_connection.close()


if __name__ == "__main__":
    main()