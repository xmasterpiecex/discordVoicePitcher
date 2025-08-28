#!/bin/zsh
FULL_PATH="$(dirname "$0")/main.py"
ACTIVATE_PATH="$(dirname "$0")/.venv/bin/activate"

PID=$(ps -aux | grep '[m]ain.py' | awk '{print $2}' | head -n 1)

if [ -n "$PID" ]; then
    echo "Sending SIGTERM to process $PID"
    kill -TERM $PID
else
    source $ACTIVATE_PATH
    nohup python3 $FULL_PATH >/dev/null 2>&1 &
    echo "Start VoiceChanger"
fi
