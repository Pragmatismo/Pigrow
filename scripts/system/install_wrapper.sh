#!/bin/bash

# Path to the wrapper script
WRAPPER_SCRIPT="./python_wrapper.sh"

# Destination directory
DEST_DIR="/usr/local/bin"

# Check if the wrapper script exists
if [ -f "$WRAPPER_SCRIPT" ]; then
    # Copy the wrapper script to the destination directory
    sudo cp "$WRAPPER_SCRIPT" "$DEST_DIR"
    sudo chmod +x "$DEST_DIR/python_wrapper.sh"
    echo "Wrapper script installed successfully."
else
    echo "Wrapper script not found at $WRAPPER_SCRIPT"
fi

# Restart cron service if necessary (optional)
# sudo systemctl restart cron
