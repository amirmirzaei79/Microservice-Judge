FROM ubuntu:22.04
RUN apt update && apt install -y gcc g++ python2 python3 python3-pip bubblewrap zip unzip
RUN pip3 install pika minio mysql-connector-python
RUN useradd -u 1234 -m judge_user
USER judge_user
WORKDIR /home/judge_user/
ENV DB_PORT=3306
ENV MQ_PORT=5672
ENV MINIO_PORT=9000
ADD ./Judge /home/judge_user/
CMD /home/judge_user/service.py
