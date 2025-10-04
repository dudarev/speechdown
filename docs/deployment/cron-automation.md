# Automated Voice Notes Transcription with Cron

This document provides instructions for setting up automated transcription of voice notes using the SpeechDown (`sd`) command via cron jobs.

## Overview

The automation setup enables continuous transcription of voice recordings in the background, processing new audio files every few minutes and storing transcriptions in date-based Markdown files within your note-taking system or vault.

## Prerequisites

### 1. Install SpeechDown via uvx

For stable automation, install SpeechDown from GitHub with a specific frozen version:

```bash
# Install or upgrade uv if not already installed
brew install uv

# Install SpeechDown from a specific version/commit for stability
# Replace <version> with a specific tag or commit hash (e.g., 0.2.5)
uvx --from git+https://github.com/dudarev/speechdown@<version> sd

# Verify installation
sd --help
```

**Note**: Using a specific version ensures the cron job continues working even if breaking changes are introduced in newer versions.

### Environment Setup

For cron jobs to work properly, you need to ensure your shell environment is correctly configured. **Cron runs with a minimal environment**, so explicit PATH and HOME configuration is essential:

```bash
# Check your current PATH includes uv tools
echo $PATH

# Check your home directory
echo $HOME

# If uv tools are not in PATH, add this to your ~/.zshrc or ~/.bash_profile:
export PATH="$HOME/.local/bin:$PATH"

# Reload your shell configuration
source ~/.zshrc  # or source ~/.bash_profile
```

**Important for cron**: The script explicitly sets `HOME` and `PATH` to ensure it works in cron's minimal environment.

### 2. Configure SpeechDown

Set up the SpeechDown configuration in your target directory:

```bash
# Navigate to your recordings directory or target directory
cd /path/to/your/voice/recordings/

# Initialize SpeechDown
sd init

# Configure output directory (adjust path as needed)
sd config --output-dir /path/to/your/notes/vault/voice/

# Set preferred languages (optional)
sd config --languages en,uk,ru
```

## Automation Script

Create the automation script at `~/bin/sd_voice_notes.sh`:

```bash
#!/bin/bash

# Automated SpeechDown Voice Notes Transcription Script
# Adapted for daily voice notes workflow with note-taking system integration

# Set HOME explicitly for cron compatibility
# Replace with your actual home directory path
HOME="/Users/YOUR_USERNAME"
export HOME

# Ensure PATH includes necessary directories for cron
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$HOME/.local/bin"

# Configuration - CUSTOMIZE THESE PATHS FOR YOUR SETUP
RECORDINGS_DIR="$HOME/Audio/Recordings"          # Your audio recordings directory
NOTES_VAULT_DIR="$HOME/Documents/Notes"          # Your notes/vault directory
VOICE_OUTPUT_DIR="$NOTES_VAULT_DIR/voice"        # Voice transcriptions subdirectory
LOCK_FILE="$HOME/sd_voice_notes.lock"
LOG_FILE="$HOME/logs/sd_voice_notes.log"
WITHIN_HOURS=24  # Process files from last 24 hours

# Function to log with timestamp
log_with_timestamp() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Check for lock file to prevent concurrent runs
if [ -e "$LOCK_FILE" ]; then
    log_with_timestamp "Another instance is already running. Exiting."
    exit 1
fi

# Create lock file
touch "$LOCK_FILE"

# Cleanup function to remove lock file
cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT SIGINT SIGTERM

log_with_timestamp "Starting SpeechDown automation"

# Ensure output directory exists
mkdir -p "$VOICE_OUTPUT_DIR"

# Change to recordings directory and run transcription
cd "$RECORDINGS_DIR" || {
    log_with_timestamp "Error: Cannot access recordings directory: $RECORDINGS_DIR"
    exit 1
}

# Initialize SpeechDown in recordings directory if not already done
if [ ! -d ".speechdown" ]; then
    log_with_timestamp "Initializing SpeechDown in recordings directory"
    sd init
fi

# Configure output directory to point to voice notes folder
sd config --output-dir "$VOICE_OUTPUT_DIR"

# Run transcription for files modified within the last N hours
log_with_timestamp "Running transcription for files modified within last $WITHIN_HOURS hours"

# Use --within-hours to only process recent files
if sd transcribe --within-hours "$WITHIN_HOURS" 2>&1 | tee -a "$LOG_FILE"; then
    log_with_timestamp "Transcription completed successfully"
else
    log_with_timestamp "Transcription failed with exit code $?"
    exit 1
fi

log_with_timestamp "SpeechDown automation completed"
```

## Script Setup

### 1. Create the script directory and file

```bash
# Create bin directory if it doesn't exist
mkdir -p ~/bin

# Create logs directory
mkdir -p ~/logs

# Create the script file
touch ~/bin/sd_voice_notes.sh

# Make it executable
chmod +x ~/bin/sd_voice_notes.sh
```

### 2. Customize the script

Edit `~/bin/sd_voice_notes.sh` and adjust the following variables:

- `HOME`: Set to your actual home directory path (e.g., `/Users/YOUR_USERNAME`)
- `RECORDINGS_DIR`: Path to your audio recordings (e.g., `$HOME/Audio/Recordings`)
- `NOTES_VAULT_DIR`: Path to your notes/vault directory (e.g., `$HOME/Documents/Notes`)
- `VOICE_OUTPUT_DIR`: Subdirectory within vault for voice transcriptions
- `WITHIN_HOURS`: Time window for processing files (24 or 48 hours recommended)

## Cron Job Configuration

### 1. Add to crontab

```bash
# Edit crontab
crontab -e

# Add the following line to run every 5 minutes:
# Note: Use absolute paths in cron jobs to avoid environment issues
*/5 * * * * /Users/YOUR_USERNAME/bin/sd_voice_notes.sh 2>&1 >> /Users/YOUR_USERNAME/logs/sd_voice_notes.log
```

### Alternative scheduling options:

```bash
# Every 10 minutes
*/10 * * * * /Users/YOUR_USERNAME/bin/sd_voice_notes.sh >> /Users/YOUR_USERNAME/logs/sd_voice_notes.log 2>&1

# Every 15 minutes
*/15 * * * * /Users/YOUR_USERNAME/bin/sd_voice_notes.sh >> /Users/YOUR_USERNAME/logs/sd_voice_notes.log 2>&1

# Every hour
0 * * * * /Users/YOUR_USERNAME/bin/sd_voice_notes.sh >> /Users/YOUR_USERNAME/logs/sd_voice_notes.log 2>&1
```

**Alternative**: You can also set the cron entry with your actual username:

```bash
# Replace 'YOUR_USERNAME' with your actual username
*/5 * * * * /Users/YOUR_USERNAME/bin/sd_voice_notes.sh 2>&1 >> /Users/YOUR_USERNAME/logs/sd_voice_notes.log
```

### 2. Verify cron job

```bash
# List current cron jobs
crontab -l

# Check cron service is running (macOS)
sudo launchctl list | grep cron
```

## Key Features

### Time-based Processing

- Uses `--within-hours` option to only process recently modified files
- Recommended values:
  - `24` hours for daily processing
  - `48` hours for more comprehensive coverage
- Avoids reprocessing old files on every run

### Automatic Daily Grouping

- SpeechDown automatically groups transcriptions by date
- Creates files named `YYYY-MM-DD.md` in the voice folder
- Each audio file becomes an H2 section with timestamp header
- Example output structure:

  ```markdown
  ## 2025-06-13 14:30:22 - recording_20250613_143022.m4a

  Transcription content here...

  ## 2025-06-13 16:45:10 - voice_memo_20250613_164510.m4a

  Another transcription...
  ```

### Timestamp Extraction

- Automatically extracts timestamps from audio filenames
- Supports multiple timestamp formats:
  - `YYYYMMDD_HHMMSS` (e.g., `20250613_143022`)
  - `YYYYMMDD HHMMSS` (e.g., `20250613 143022`)
  - `YYMMDD_HHMMSS` (e.g., `250613_143022`)
- Falls back to file modification time for unparseable filenames

### Conflict Prevention

- Uses lock file mechanism to prevent concurrent executions
- Safe for frequent cron scheduling (every 5 minutes)
- Comprehensive logging for monitoring and debugging

## Monitoring and Maintenance

### Log Monitoring

```bash
# View recent log entries
tail -f ~/logs/sd_voice_notes.log

# View last 50 log lines
tail -50 ~/logs/sd_voice_notes.log

# Search for errors
grep -i error ~/logs/sd_voice_notes.log
```

### Manual Testing

```bash
# Test the script manually
~/bin/sd_voice_notes.sh

# Test with minimal environment (similar to cron)
env -i HOME="/Users/YOUR_USERNAME" PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/Users/YOUR_USERNAME/.local/bin" ~/bin/sd_voice_notes.sh

# Test with dry run (modify script temporarily to add --dry-run flag)
# This helps verify the setup without making actual changes

# Debug what cron environment looks like
/usr/bin/env > /tmp/normal-env.txt
# Then add this to crontab temporarily:
# * * * * * /usr/bin/env > /tmp/cron-env.txt
# Compare the two files to see differences
```

### Log Rotation

Consider setting up log rotation to prevent log files from growing too large:

```bash
# Add to a daily cleanup script or cron job
# Keep only last 30 days of logs
find ~/logs -name "sd_voice_notes.log*" -mtime +30 -delete
```

## Troubleshooting

### Common Issues

1. **Permission denied**

   ```bash
   chmod +x ~/bin/sd_voice_notes.sh
   ```

2. **Permission denied**

   ```bash
   chmod +x ~/bin/sd_voice_notes.sh
   ```

3. **Command not found (sd)**

   - Verify uv installation and PATH configuration
   - Check that `$HOME/.local/bin` is in PATH
   - Run `uv tool list` to verify SpeechDown is installed
   - **Cron-specific**: Ensure the script sets PATH explicitly (see script example)

3. **Lock file issues**

   ```bash
   # Remove stale lock file if process crashed
   rm ~/sd_voice_notes.lock
   # Or with absolute path:
   rm /Users/YOUR_USERNAME/sd_voice_notes.lock
   ```

4. **Directory access errors**

   - Verify all paths in the script exist and are accessible
   - Check file sync status if using cloud storage
   - **Cron-specific**: Use absolute paths instead of relative paths

5. **Environment variable issues (cron-specific)**

   ```bash
   # Test what environment cron sees:
   # Add this temporary line to crontab to debug:
   * * * * * env > /tmp/cron-env.txt

   # Then check the file after a minute:
   cat /tmp/cron-env.txt

   # Compare with your normal shell environment:
   env
   ```

### Debugging

Enable more verbose logging by modifying the script:

```bash
# Add debug flag to sd transcribe command
sd transcribe --within-hours "$WITHIN_HOURS" --debug 2>&1 | tee -a "$LOG_FILE"
```

## Migration from Existing Voice Automation

If migrating from an existing voice transcription automation setup:

1. **Backup existing automation**

   ```bash
   # Backup your existing voice automation script
   cp /path/to/your/existing/voice_script.sh /path/to/your/existing/voice_script.sh.backup
   ```

2. **Update crontab**

   ```bash
   # Comment out old entry (example)
   # */5 * * * * /path/to/old/voice_script.sh 2>&1 > /path/to/old/log

   # Add new entry
   */5 * * * * /Users/YOUR_USERNAME/bin/sd_voice_notes.sh 2>&1 >> /Users/YOUR_USERNAME/logs/sd_voice_notes.log
   ```

3. **Parallel testing**
   - Run both systems in parallel initially
   - Compare outputs to ensure consistency
   - Disable old system once confident in new setup

## Benefits Over Previous Setup

- **No date parameter handling**: Uses time-based filtering instead
- **Automatic language detection**: Supports multiple languages
- **Better timestamp extraction**: More robust filename parsing
- **Daily file grouping**: Automatic organization by date
- **Improved error handling**: Better logging and recovery
- **Stable versioning**: Pinned installation via uvx
