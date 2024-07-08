#!/bin/bash

# Path to your virtual environment
VENV_PATH="$HOME/venv_pigrow"

# Check if the virtual environment directory exists
if [ -d "$VENV_PATH" ]; then
    # Activate the virtual environment
    source "$VENV_PATH/bin/activate"
    exec python "$@"
else
    # Fall back to the system Python if the virtual environment does not exist
    exec /usr/bin/python3 "$@"
fi
