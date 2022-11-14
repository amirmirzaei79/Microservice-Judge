#!/bin/bash
PID=`pgrep service.py | head -1`
kill -SIGTERM $PID
wait $PID
