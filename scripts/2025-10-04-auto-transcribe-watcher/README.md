# Auto-Transcribe File Watcher Scripts

This directory contains scripts and configuration files for automatically transcribing audio files when they are added to a watched folder.

**Key Feature:** The watcher service automatically starts when your system boots and continues running in the background without any manual intervention.

## Features

- 🚀 **Auto-start on system boot** - Runs automatically when your Mac starts
- 🔄 **Auto-restart on failure** - Recovers automatically if the process crashes
- ⚡ **Real-time monitoring** - Instant detection of new audio files (no polling delays)
- 📝 **Complete logging** - Tracks all transcription activity
- 🎯 **Configurable** - Choose which directory to watch and which audio formats to process

## Contents

- `watcher.sh` - Main file watching script using fswatch
- `install.sh` - Installation script for setting up the LaunchAgent
- `uninstall.sh` - Script to remove the LaunchAgent
- `com.speechdown.watcher.plist.template` - LaunchAgent configuration template (includes auto-start settings)
- `watchdog.sh` - Watchdog script that monitors the watcher
- `install_watchdog.sh` - Sets up cron job for watchdog monitoring (optional)
- `uninstall_watchdog.sh` - Removes watchdog cron job

## File Locations

Following the established pattern in your infrastructure:
- **Logs**: `~/logs/speechdown_watcher.log` (visible logs directory)
- **Lock file**: `~/speechdown_watcher.lock` (contains watcher PID)
- **Watchdog log**: `~/logs/speechdown_watchdog.log` (optional monitoring)

**Note:** The watcher passes all new files to `sd`, which intelligently handles audio vs non-audio files. Obvious temporary files (like `.file.ext.temp123` and `.db-journal`) are silently skipped to reduce noise. Set `SPEECHDOWN_WATCHER_VERBOSE=true` for more detailed logging.

## Documentation

For full documentation, rationale, and research findings, see:
- [Research Document](../../docs/research/2025-10-04-auto-transcribe-watcher.md)

## Requirements

- macOS 10.10+
- fswatch (install via `brew install fswatch`)
- speechdown CLI installed and configured

## Quick Start

### Installation

1. **Install fswatch** (if not already installed):
   ```bash
   brew install fswatch
   ```

2. **Run the installation script**:
   ```bash
   cd scripts/2025-10-04-auto-transcribe-watcher
   ./install.sh
   ```

3. **Follow the prompts** to configure:
   - Directory to watch (default: `~/Downloads`)
   - The script will automatically configure auto-start

4. **Done!** The watcher is now running and will automatically start when your system boots.

### Optional: Install Watchdog (Extra Reliability)

For additional safety, install the watchdog monitor:

```bash
./install_watchdog.sh
```

This adds a cron job that checks every 15 minutes if the watcher is running, and restarts it if needed. This provides a backup to the LaunchAgent's built-in restart mechanism.

### Verifying Auto-Start

To confirm the watcher is installed to start automatically:

```bash
# Check if the service is running
launchctl list | grep speechdown

# View the LaunchAgent configuration
cat ~/Library/LaunchAgents/com.speechdown.watcher.plist
```

Look for these key settings in the plist:
- `<key>RunAtLoad</key><true/>` - Starts on boot
- `<key>KeepAlive</key><true/>` - Auto-restarts if crashed

### Testing

1. Copy an audio file to your watched directory:
   ```bash
   cp ~/some-audio-file.m4a ~/Downloads/
   ```

2. Watch the logs to see transcription happen:
   ```bash
   tail -f ~/logs/speechdown_watcher.log
   ```

3. Restart your computer and verify the service auto-starts:
   ```bash
   # After reboot, check if service is running
   launchctl list | grep speechdown
   ```

## Usage

### Viewing Logs

```bash
# Real-time log monitoring
tail -f ~/logs/speechdown_watcher.log

# View recent activity
tail -50 ~/logs/speechdown_watcher.log

# View all logs
cat ~/logs/speechdown_watcher.log

# Check lock file (contains PID of running watcher)
cat ~/speechdown_watcher.lock
```

### Managing the Service

```bash
# Check status
launchctl list | grep speechdown

# Stop the watcher (temporary - will restart on next boot)
launchctl unload ~/Library/LaunchAgents/com.speechdown.watcher.plist

# Start the watcher manually
launchctl load ~/Library/LaunchAgents/com.speechdown.watcher.plist

# Restart the watcher
launchctl unload ~/Library/LaunchAgents/com.speechdown.watcher.plist
launchctl load ~/Library/LaunchAgents/com.speechdown.watcher.plist
```

### Watchdog Monitoring (Optional)

The watchdog provides an extra layer of reliability:

```bash
# Install watchdog (adds cron job)
./install_watchdog.sh

# View watchdog logs (only logs when action is taken)
tail -f ~/logs/speechdown_watchdog.log

# Check watchdog cron job
crontab -l | grep watchdog

# Manually run watchdog check
./watchdog.sh

# Uninstall watchdog
./uninstall_watchdog.sh
```

**How it works:**
- Runs every 15 minutes via cron
- Checks if watcher is running (via LaunchAgent and lock file)
- If watcher is down, automatically restarts it
- Logs only when issues are detected or actions taken
- Complements LaunchAgent's auto-restart (belt and suspenders)

### Uninstallation

To completely remove the auto-start service:

```bash
# Remove watcher service
./uninstall.sh

# Remove watchdog (if installed)
./uninstall_watchdog.sh
```

This will:
- Stop the running service
- Remove the LaunchAgent configuration
- Remove watchdog cron job (if installed)
- Prevent auto-start on future boots
- Keep your log files (optional manual cleanup)

## Configuration

The watcher can be configured via environment variables in the LaunchAgent plist:

- `SPEECHDOWN_WATCH_DIR` - Directory to monitor (default: `~/Downloads`)
- `SPEECHDOWN_WATCHER_LOG` - Log file location (default: `~/logs/speechdown_watcher.log`)
- `SPEECHDOWN_WATCHER_LOCK` - Lock file location (default: `~/speechdown_watcher.lock`)
- `SPEECHDOWN_WATCHER_VERBOSE` - Enable verbose logging including temp files (default: `false`)
- `SPEECHDOWN_WITHIN_HOURS` - Only process files modified within this many hours (default: `48`)
- `SPEECHDOWN_CMD` - Path to sd command (default: `sd`)

To change configuration:
1. Edit `~/Library/LaunchAgents/com.speechdown.watcher.plist`
2. Restart the service (unload then load)

## Troubleshooting

### Service not starting after reboot

```bash
# Check if LaunchAgent file exists
ls -l ~/Library/LaunchAgents/com.speechdown.watcher.plist

# Check for errors in system logs
log show --predicate 'subsystem == "com.apple.launchd"' --last 1h | grep speechdown
```

### Files not being transcribed

```bash
# Check if service is running
launchctl list | grep speechdown

# Check lock file
if [ -f ~/speechdown_watcher.lock ]; then
    echo "Watcher PID: $(cat ~/speechdown_watcher.lock)"
    ps -p $(cat ~/speechdown_watcher.lock)
fi

# Check logs for errors
tail -50 ~/logs/speechdown_watcher.log

# Verify speechdown command works
which sd
sd --version
```

### Manually testing the watcher script

You can run the watcher script directly (without LaunchAgent) for debugging:

```bash
# Stop the service first
launchctl unload ~/Library/LaunchAgents/com.speechdown.watcher.plist

# Run manually with custom settings
SPEECHDOWN_WATCH_DIR=~/Downloads ./watcher.sh

# Press Ctrl+C to stop
```

## Security Notes

- The watcher runs with your user permissions
- It only monitors the directory you specify during installation
- All transcriptions use your existing speechdown configuration
- Logs are stored in `~/logs/`
- Lock file in `~/speechdown_watcher.lock` contains the watcher's process ID
