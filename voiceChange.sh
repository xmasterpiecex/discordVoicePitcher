#!/bin/zsh
FULL_PATH="$HOME/forfun/probe/pythonVoiceChanger/main.py"

PID=$(ps -aux | grep '[m]ain.py' | awk '{print $2}' | head -n 1)

if [ -n "$PID" ]; then
    echo "Sending SIGTERM to process $PID"
    kill -TERM $PID
else
    nohup python3 "$FULL_PATH" >/dev/null 2>&1 &
    echo "Python script not running."
fi
