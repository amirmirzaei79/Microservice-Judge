from ctypes import util
import unittest

import os
import shutil

import config
import utils

class TestCompile(unittest.TestCase):
    def test_c_compile(self):
        os.makedirs(config.working_dir, exist_ok=True)
        os.makedirs(config.code_dir, exist_ok=True)

        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/test_files/compile/success.c", config.code_dir)

        compile_result = utils.compile("success.c", "C")
        self.assertEqual(compile_result, True)

        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/test_files/compile/fail.c", config.code_dir)

        compile_result= utils.compile("fail.c", "C")
        self.assertEqual(compile_result, False)

        shutil.rmtree(config.code_dir)


    def test_python_compile(self):
        os.makedirs(config.working_dir, exist_ok=True)
        os.makedirs(config.code_dir, exist_ok=True)

        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/test_files/compile/success.py", config.code_dir)

        compile_result = utils.compile("success.py", "Python3")
        self.assertEqual(compile_result, True)

        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/test_files/compile/fail.py", config.code_dir)

        compile_result = utils.compile("fail.py", "Python3")
        self.assertEqual(compile_result, False)

        shutil.rmtree(config.code_dir)

    
class TestRunSingle(unittest.TestCase):
    def test_judgement(self):
        os.makedirs(config.working_dir, exist_ok=True)
        os.makedirs(config.code_dir, exist_ok=True)
        os.makedirs(config.testcases_dir, exist_ok=True)
        os.makedirs(config.tester_dir, exist_ok=True)
        os.makedirs(config.program_out_dir, exist_ok=True)

        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/test_files/single_test/correct.py", config.code_dir) # Correct Answer
        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/test_files/single_test/wrong.py", config.code_dir) # Wrong Answer
        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/test_files/single_test/runtime.py", config.code_dir) # Runtime Error
        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/test_files/single_test/memorylimit.py", config.code_dir) # Memory Limit Exceeded
        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/test_files/single_test/timelimit.py", config.code_dir) # Timelimit exceeded

        shutil.copytree(os.path.dirname(os.path.abspath(__name__)) + "/test_files/single_test/testcase", config.testcases_dir, dirs_exist_ok=True)
        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/default_tester/default_tester.py", config.tester_dir)

        result = utils.run_test("correct.py", "Python3", 1, 15000, 1, "default_tester.py")
        self.assertEqual(result, (True, "Correct Answer"))
        result = utils.run_test("wrong.py", "Python3", 1, 15000, 1, "default_tester.py")
        self.assertEqual(result, (False, "Wrong Answer"))
        result = utils.run_test("memorylimit.py", "Python3", 1, 1500, 1, "default_tester.py")
        self.assertEqual(result, (False, "Runtime Error"))
        result = utils.run_test("runtime.py", "Python3", 1, 15000, 1, "default_tester.py")
        self.assertEqual(result, (False, "Runtime Error"))
        result = utils.run_test("timelimit.py", "Python3", 1, 15000, 1, "default_tester.py")
        self.assertEqual(result, (False, "Time Limit Exceeded"))
        
        shutil.rmtree(config.working_dir)


class TestRun(unittest.TestCase):
    def test_correct_answer(self):
        os.makedirs(config.working_dir, exist_ok=True)
        os.makedirs(config.code_dir, exist_ok=True)
        os.makedirs(config.testcases_dir, exist_ok=True)
        os.makedirs(config.tester_dir, exist_ok=True)
        os.makedirs(config.program_out_dir, exist_ok=True)

        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/test_files/full_test/power.py", config.code_dir)

        shutil.copytree(os.path.dirname(os.path.abspath(__name__)) + "/test_files/full_test/testcases", config.testcases_dir, dirs_exist_ok=True)
        shutil.copy(os.path.dirname(os.path.abspath(__name__)) + "/default_tester/default_tester.py", config.tester_dir)

        result = utils.run_testcases("power.py", "Python3", 1, 64000, "default_tester.py")
        self.assertEqual(result, 0.75)
        
        shutil.rmtree(config.working_dir)


if __name__ == "__main__":
    unittest.main()