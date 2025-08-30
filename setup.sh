#!/bin/zsh
set -e

echo "Creating virtual environment"
python3 -m venv ./.venv

echo "Activating virtual environment"
source ".venv/bin/activate"

echo "Installing dependencies"
pip install --upgrade pip
pip install -r requirement.txt
