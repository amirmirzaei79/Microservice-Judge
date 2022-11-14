import os

import config


def compile(file_path: str, language: str):
    log_file = open(config.log_file, "a")
    log_file.write("-> Compiling: \n")
    log_file.close()

    compile_command = config.compile_sandbox + " /" + config.scripts_dir + \
                      "/exec_in_dir.sh /" + config.code_dir + " " + \
                      config.compiler[language] + " " + file_path + \
                      " >>" + config.log_file + " 2>&1"
    compile_result = os.system(compile_command)

    return (compile_result == 0)


def run_test(file_path, language, time_limit, memory_limit, test_number, 
             tester_path):
    log_file = open(config.log_file, "a")
    log_file.write(f"\n-> Test Number {test_number}: \n")
    log_file.close()
    
    in_path = config.testcases_dir + f"/in/input{test_number}.txt"
    out_path = config.testcases_dir + f"/out/output{test_number}.txt"
    produced_out_path = config.program_out_dir + f"/output{test_number}.txt"
    run_command = config.run_sandbox + " /" + config.scripts_dir + \
                  f"/run_code.sh /{config.code_dir} {time_limit} {memory_limit} " + \
                  config.run_command[language](file_path) + \
                  f" <{in_path} >{produced_out_path} 2>/dev/null"

    exitstatus = os.system(run_command)
    exitcode = exitstatus // 256

    # exitcode
    # 0: Success
    # 124: Timeout
    # rest: Runtime Error (Including memory error)

    if exitcode == 0:
        tester_command = config.tester_sandbox + " /" + config.tester_dir + \
                         f"/{tester_path} /{in_path} /{out_path} /{produced_out_path}" + \
                         " 1>>" + config.log_file + " 2>&1"
        tester_exitcode = os.system(tester_command)

        if tester_exitcode == 0:
            return True, "Correct Answer"
        else:
            return False, "Wrong Answer"
    elif exitcode == 124:
        return False, "Time Limit Exceeded"
    else:
        return False, "Runtime Error"


def run_testcases(file_path, language, time_limit, memory_limit, tester_path):
    number_of_test = len(os.listdir(config.testcases_dir + "/in"))

    number_of_passed_tests = 0

    results_file = open(config.results_file, "w")
    for i in range(1, number_of_test + 1):
        test_passed, status = run_test(file_path, language, time_limit, memory_limit, i, tester_path)
        results_file.write(f"Test {i}:\n")
        results_file.write(status + "\n\n")

        number_of_passed_tests += 1 if test_passed else 0

    results_file.close()

    return number_of_passed_tests / number_of_test