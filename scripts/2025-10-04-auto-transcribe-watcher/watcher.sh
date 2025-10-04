#!/usr/bin/env zsh

# SpeechDown Auto-Transcribe File Watcher
# Monitors a directory for new audio files and automatically transcribes them

set -euo pipefail

# Configuration
WATCH_DIR="${SPEECHDOWN_WATCH_DIR:-$HOME/Downloads}"
LOG_FILE="${SPEECHDOWN_WATCHER_LOG:-$HOME/logs/speechdown_watcher.log}"
LOCK_FILE="${SPEECHDOWN_WATCHER_LOCK:-$HOME/speechdown_watcher.lock}"
VERBOSE_LOGGING="${SPEECHDOWN_WATCHER_VERBOSE:-false}"
WITHIN_HOURS="${SPEECHDOWN_WITHIN_HOURS:-48}"
SPEECHDOWN_CMD="${SPEECHDOWN_CMD:-sd}"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Check if fswatch is installed
if ! command -v fswatch &> /dev/null; then
    log "ERROR: fswatch is not installed. Install it with: brew install fswatch"
    exit 1
fi

# Check if speechdown is available
if ! command -v "$SPEECHDOWN_CMD" &> /dev/null; then
    log "ERROR: speechdown command not found. Make sure it's installed and in PATH."
    exit 1
fi

# Check if watch directory exists
if [[ ! -d "$WATCH_DIR" ]]; then
    log "ERROR: Watch directory does not exist: $WATCH_DIR"
    exit 1
fi

# Check if another instance is already running
if [[ -f "$LOCK_FILE" ]]; then
    existing_pid=$(cat "$LOCK_FILE" 2>/dev/null)
    if [[ -n "$existing_pid" ]] && ps -p "$existing_pid" > /dev/null 2>&1; then
        log "ERROR: Another watcher instance is already running (PID: $existing_pid)"
        log "If you're sure no watcher is running, remove the lock file: rm $LOCK_FILE"
        exit 1
    else
        log "WARNING: Removing stale lock file (PID $existing_pid no longer exists)"
        rm -f "$LOCK_FILE"
    fi
fi

# Create lock file
echo $$ > "$LOCK_FILE"

log "Starting SpeechDown file watcher (PID: $$)"
log "Watching directory: $WATCH_DIR"
log "Command: $SPEECHDOWN_CMD transcribe --within-hours $WITHIN_HOURS"
log "Lock file: $LOCK_FILE"
log "Note: Only processing files from the last $WITHIN_HOURS hours"

# Process a new file event
process_file() {
    local file="$1"
    
    # Skip obvious temp/system files
    if [[ "$file" =~ \.db-journal$ ]] || [[ "$file" =~ \.[a-zA-Z0-9]{8,}$ ]]; then
        return
    fi
    
    # Check if it's an audio file
    if [[ ! "$file" =~ \.(m4a|mp3|wav|flac|ogg|aac|mp4)$ ]]; then
        if [[ "$VERBOSE_LOGGING" == "true" ]]; then
            log "Skipping non-audio file: $file"
        fi
        return
    fi
    
    # Check if file still exists
    if [[ ! -f "$file" ]]; then
        if [[ "$VERBOSE_LOGGING" == "true" ]]; then
            log "File no longer exists: $file"
        fi
        return
    fi
    
    # Wait to ensure file is fully written
    sleep 2
    
    log "New audio file detected: $file"
    
    # Run sd transcribe in the watch directory
    # sd works on the entire directory, so we cd there first
    cd "$WATCH_DIR" || {
        log "ERROR: Cannot cd to $WATCH_DIR"
        return
    }
    
    log "Running: cd $WATCH_DIR && $SPEECHDOWN_CMD transcribe --within-hours $WITHIN_HOURS"
    log "Transcription started (processing files from last $WITHIN_HOURS hours)..."
    
    # Use tee to capture output to log while still getting exit code
    if "$SPEECHDOWN_CMD" transcribe --within-hours "$WITHIN_HOURS" 2>&1 | tee -a "$LOG_FILE" > /dev/null; then
        log "✓ Transcription completed successfully"
    else
        exit_code=$?
        log "✗ Transcription failed with exit code: $exit_code"
    fi
}

# Trap signals for graceful shutdown
cleanup() {
    log "Stopping file watcher"
    rm -f "$LOCK_FILE"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Start watching with fswatch
# Watch for Created, Updated, and Renamed events to catch Dropbox syncs
log "Watcher is now active. Press Ctrl+C to stop."

fswatch -0 -r --event Created --event Updated --event Renamed "$WATCH_DIR" | while IFS= read -r -d '' file; do
    process_file "$file"
done
