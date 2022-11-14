#!/bin/bash

# $0 <directory_path> <command>

dir_path=$1
shift

cd $dir_path

$@
