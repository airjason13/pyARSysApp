#!/bin/sh

# 1. Forcefully terminate any existing audio processes
pkill -9 -x wireplumber 2>/dev/null
pkill -9 -x pipewire 2>/dev/null

# 2. Set up the environment
# Use current user ID to define runtime directory (e.g., /run/user/0 for root)
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}
mkdir -p "$XDG_RUNTIME_DIR"
# PipeWire requires strict permissions (700) on the runtime directory
chmod 700 "$XDG_RUNTIME_DIR"

# 3. Start PipeWire core daemon
# Redirect output to log file and run in background
nohup pipewire > /tmp/pipewire.log 2>&1 &
sleep 0.5

# Defensive check: Ensure PipeWire is actually running
if ! pgrep -x pipewire > /dev/null; then
    echo "Error: Pipewire failed to start! Check /tmp/pipewire.log"
    exit 1
fi

# 4. Start WirePlumber session manager
nohup wireplumber > /tmp/wireplumber.log 2>&1 &
sleep 0.5

# Defensive check: Ensure WirePlumber is actually running
if ! pgrep -x wireplumber > /dev/null; then
    echo "Error: WirePlumber failed to start! Check /tmp/wireplumber.log"
    exit 1
fi

echo "Audio services started successfully."