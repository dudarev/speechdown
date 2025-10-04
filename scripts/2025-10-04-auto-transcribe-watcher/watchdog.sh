#!/usr/bin/env zsh

# SpeechDown Watcher Watchdog Script
# Monitors the file watcher service and restarts it if it's not running
# Designed to run via cron as a safety net for LaunchAgent

set -euo pipefail

# Configuration
PLIST_NAME="com.speechdown.watcher.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"
LOCK_FILE="$HOME/speechdown_watcher.lock"
LOG_FILE="$HOME/logs/speechdown_watchdog.log"
WATCHER_SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

# Check if watcher is running
is_watcher_running() {
    # Method 1: Check if LaunchAgent is loaded
    if launchctl list | grep -q "com.speechdown.watcher"; then
        return 0  # Running
    fi
    
    # Method 2: Check lock file and verify process
    if [[ -f "$LOCK_FILE" ]]; then
        local pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if [[ -n "$pid" ]] && ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Running
        fi
    fi
    
    return 1  # Not running
}

# Start the watcher
start_watcher() {
    log "Attempting to start watcher..."
    
    # Check if LaunchAgent plist exists
    if [[ ! -f "$PLIST_PATH" ]]; then
        log "ERROR: LaunchAgent plist not found at $PLIST_PATH"
        log "Run install.sh to set up the watcher first"
        return 1
    fi
    
    # Load the LaunchAgent
    if launchctl load "$PLIST_PATH" 2>> "$LOG_FILE"; then
        log "Successfully started watcher via LaunchAgent"
        return 0
    else
        log "ERROR: Failed to load LaunchAgent"
        return 1
    fi
}

# Main watchdog logic
main() {
    if is_watcher_running; then
        # Watcher is running, all good (no log spam)
        exit 0
    else
        # Watcher is not running, try to start it
        log "WARNING: Watcher is not running!"
        
        # Clean up stale lock file if exists
        if [[ -f "$LOCK_FILE" ]]; then
            log "Removing stale lock file"
            rm -f "$LOCK_FILE"
        fi
        
        if start_watcher; then
            log "Watcher recovery successful"
        else
            log "ERROR: Failed to recover watcher"
            exit 1
        fi
    fi
}

# Run watchdog
main
