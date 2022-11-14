#!/usr/bin/python3
import sys

test_out = open(sys.argv[2], "r")
user_out = open(sys.argv[3], "r")

test_out_lines = test_out.readlines()
user_out_lines = user_out.readlines()

if len(test_out_lines) != len(user_out_lines):
    exit(1)

for i in range(len(test_out_lines)):
    to_fields = test_out_lines[i].split(' ')
    uo_fields = user_out_lines[i].split(' ')

    if (len(to_fields) != len(uo_fields)):
        exit(1)
    
    for j in range(len(to_fields)):
        if to_fields[j] != uo_fields[j]:
            exit(1)

exit(0)