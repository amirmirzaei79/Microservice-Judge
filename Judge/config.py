import os


working_dir = "working"
log_file = working_dir + "/log.txt"
results_file = working_dir + "/results.txt"
code_dir = working_dir + "/code"
scripts_dir = os.path.dirname(os.path.abspath(__name__)) + "/scripts"
testcases_dir = working_dir + "/testcases"
tester_dir = testcases_dir
program_out_dir = working_dir + "/program_output"

# bubblewrap-0.4.0 --- default in ubuntu 20.04 software repositories
compile_sandbox = "bwrap --dev /dev --ro-bind /proc /proc --symlink /usr/bin /bin " + \
                  "--symlink /usr/bin /sbin --symlink /usr/lib /lib " + \
                  "--symlink /usr/lib64 /lib64 --ro-bind /usr /usr " + \
                  "--ro-bind /etc /etc --ro-bind " + scripts_dir + " /" + scripts_dir + " " + \
                  "--unshare-all --clearenv --bind " + code_dir + " /" + code_dir
run_sandbox = "bwrap --dev /dev --ro-bind /proc /proc --symlink /usr/bin /bin " + \
              "--symlink /usr/bin /sbin --symlink /usr/lib /lib " + \
              "--symlink /usr/lib64 /lib64 --ro-bind /usr /usr " + \
              "--ro-bind /etc /etc --ro-bind " + scripts_dir + " /" + scripts_dir + " " + \
              "--unshare-all --clearenv --ro-bind " + code_dir + " /" + code_dir
tester_sandbox = "bwrap --dev /dev --ro-bind /proc /proc --symlink /usr/bin /bin " + \
                 "--symlink /usr/bin /sbin --symlink /usr/lib /lib " + \
                 "--symlink /usr/lib64 /lib64 --ro-bind /usr /usr " + \
                 "--ro-bind /etc /etc --ro-bind " + testcases_dir + " /" + testcases_dir + " " + \
                 "--ro-bind " + code_dir + " /" + code_dir + " --unshare-all --clearenv " + \
                 "--ro-bind " + tester_dir + " /" + testcases_dir + " --ro-bind " + program_out_dir + \
                 " /" + program_out_dir

compiler = {
    "C" : "gcc -o compiled.out",
    "C++": "g++ -o compiled.out",
    "Python2": "python2 -m py_compile",
    "Python3": "python3 -m py_compile",
    # "Java": "javac "
}

run_command = {
    "C" : lambda file_path: os.path.dirname(file_path) + "compiled.out",
    "C++": lambda file_path: os.path.dirname(file_path) + "compiled.out",
    "Python2": lambda file_path: "python2 " + file_path,
    "Python3": lambda file_path: "python3 " + file_path,
    # "Java": lambda file_path: "java " + os.path.splitext(file_path)[0]
}

default_tester = ""
