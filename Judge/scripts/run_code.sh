#!/bin/bash

# $0 <code_dir> <time_limit(s)> <memory_limit(KB)> <command>

code_dir=$1
shift
time_limit=$1
shift
memory_limit=$1
shift
command=$@

cd $code_dir

ulimit -m $memory_limit
ulimit -s $memory_limit
ulimit -v $memory_limit
ulimit -f $memory_limit

time_limit="$time_limit"s

timeout $time_limit $command
