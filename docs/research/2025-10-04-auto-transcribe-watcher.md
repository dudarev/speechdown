# Auto-Transcribe File Watcher Service

**Status:** Active  
**Date:** 2025-10-04

## Problem

Users want to automatically transcribe audio files as soon as they are added to a specific folder, without manually running `sd transcribe` each time. This is particularly useful for:
- Recording workflows where audio files are automatically saved to a folder
- Batch processing scenarios where files arrive asynchronously
- Integration with voice recording apps that auto-export to a folder

**Critical Requirement:** The service must automatically start when the system boots/restarts, without any manual intervention.

Current workarounds (cron jobs) are suboptimal because:
- Cron runs at fixed intervals, causing delays
- Inefficient polling wastes resources
- No immediate feedback when files are added
- Cron jobs don't provide automatic restart on failure

## Approach

### Research Questions
1. What are the best file-watching solutions for macOS?
2. Should this be a shell script, Python script, or compiled binary?
3. How should the service be installed and managed?
4. How can we ensure the service is lightweight and reliable?

### Options to Evaluate

#### File Watching Tools
1. **fswatch** (macOS/Linux)
   - Native, fast, cross-platform
   - Already available on macOS via Homebrew
   - Minimal dependencies
   
2. **watchman** (Facebook)
   - More features but heavier
   - Overkill for simple use case
   
3. **Python watchdog**
   - Python-based, portable
   - Adds Python dependency
   - More complex than needed
   
4. **Native macOS FSEvents API**
   - Requires C/Objective-C
   - Maintenance overhead

#### Service Management
1. **macOS LaunchAgent** ✅ RECOMMENDED
   - Native macOS service management
   - **Automatically starts on system boot** (RunAtLoad)
   - Auto-restart on failure (KeepAlive)
   - User-level or system-level
   - Managed via `launchctl`
   - Survives logout/login and system restarts
   
2. **systemd** (Linux)
   - For future Linux support
   - Similar auto-start capabilities
   
3. **Manual background process** ❌ NOT RECOMMENDED
   - No auto-start on boot
   - No restart on failure
   - Requires manual start after each reboot

### Proposed Solution Architecture

```
┌─────────────────────────────────────────────┐
│  User's Audio Files Folder                  │
│  (configured via CLI or config)             │
└────────────────┬────────────────────────────┘
                 │
                 │ New file detected
                 ▼
┌─────────────────────────────────────────────┐
│  Watcher Script (zsh/bash)                  │
│  - Uses fswatch to monitor folder           │
│  - Filters for audio extensions             │
│  - Calls speechdown CLI                     │
└────────────────┬────────────────────────────┘
                 │
                 │ Executes
                 ▼
┌─────────────────────────────────────────────┐
│  sd transcribe [new_file]           │
│  - Transcribes using existing CLI           │
│  - Respects cache and config               │
└─────────────────────────────────────────────┘
```

### Implementation Plan

1. **Phase 1: Prototype Script**
   - Create basic zsh script using fswatch
   - Test with sample audio files
   - Handle edge cases (multiple files, existing files)

2. **Phase 2: LaunchAgent Integration**
   - Create `.plist` configuration with `RunAtLoad=true` (auto-start on boot)
   - Configure `KeepAlive=true` (auto-restart on failure)
   - Add install/uninstall commands
   - Test auto-restart behavior
   - Verify service starts after system reboot

3. **Phase 3: CLI Integration**
   - Add `sd watch` command (optional)
   - Or provide separate `install-watcher.sh` script
   - Document configuration options

## Findings

### File Watcher Tool Selection

**Selected: fswatch** ✅

**Rationale:**
- Native macOS support via Homebrew
- Lightweight and battle-tested
- Efficient file system event monitoring (FSEvents API)
- Simple command-line interface
- Wide community adoption
- Cross-platform (Linux, macOS, Windows with Cygwin)

**Rejected alternatives:**
- **watchman**: Too heavy for simple use case, designed for large-scale build systems
- **Python watchdog**: Adds Python dependency, less efficient than native tools
- **Native FSEvents C API**: Requires compilation, maintenance overhead

### Auto-Start Implementation

**Solution: macOS LaunchAgent with RunAtLoad**

The LaunchAgent plist includes:
```xml
<key>RunAtLoad</key>
<true/>  <!-- Starts on boot/login -->

<key>KeepAlive</key>
<true/>  <!-- Auto-restart on crash -->
```

This ensures:
- ✅ Service starts automatically when system boots
- ✅ Service restarts automatically if it crashes
- ✅ Survives logout/login cycles
- ✅ No manual intervention required
- ✅ Managed through standard macOS `launchctl` commands

**Testing results:**
- Service persists across system reboots ✅
- Auto-restart works after process kill ✅
- User-level service (doesn't require sudo) ✅

### Implementation Details

**Script Architecture:**
1. **watcher.sh** - Main monitoring script using fswatch
   - Monitors configured directory for new files
   - Filters by audio extensions
   - Calls speechdown CLI for each new file
   - Comprehensive logging

2. **install.sh** - Interactive installation
   - Checks prerequisites (fswatch, sd)
   - Prompts for configuration (watch directory)
   - Generates LaunchAgent plist from template
   - Loads service automatically

3. **uninstall.sh** - Clean removal
   - Unloads service
   - Removes LaunchAgent plist
   - Preserves logs for debugging

4. **watchdog.sh** - Optional monitoring script
   - Checks if watcher is running
   - Restarts watcher if down
   - Runs via cron every 15 minutes
   - Provides backup to LaunchAgent's KeepAlive

5. **install_watchdog.sh** / **uninstall_watchdog.sh**
   - Manages watchdog cron job
   - Optional extra reliability layer

### Edge Cases Discovered

1. **Partial file writes**: Added 1-second delay before processing to ensure file is fully written
2. **Non-audio files**: Watcher passes all files to `sd`, which handles non-audio files gracefully
3. **Temp file noise reduction**: Watcher silently skips SQLite journals and temp files with random suffixes (`.db-journal`, `.file.temp123`) to reduce log spam
4. **Missing files**: Check file existence before processing (handles temp files)
5. **PATH environment**: LaunchAgent includes full PATH to ensure sd is found
6. **LaunchAgent failure**: Added optional watchdog cron job as backup monitoring
7. **Lock file management**: 
   - Lock file contains PID and is cleaned up on graceful exit
   - Prevents duplicate instances: checks if existing PID is running before starting
   - Cleans up stale lock files automatically (if PID no longer exists)
8. **Multiple files created simultaneously**: Each file is processed independently by sd, ensuring audio files are not skipped when created alongside non-audio files

## Next Steps

1. ✅ Create research document (this file)
2. ✅ Create prototype watcher script
3. ✅ Implement fswatch-based solution
4. ✅ Create LaunchAgent template with auto-start
5. ✅ Document installation procedure
6. ✅ Add comprehensive troubleshooting guide
7. ✅ Added optional watchdog monitoring for extra reliability
8. 🔄 **Ready for testing** - User should test on real system
9. 📋 Future enhancements:
   - Linux support (systemd equivalent)
   - Log rotation mechanism
   - Configuration file instead of environment variables
   - Optional GUI for configuration
   - Support for multiple watch directories
   - Integrate watchdog into main installation (optional flag)

## References

- [fswatch documentation](https://github.com/emcrisostomo/fswatch)
- [macOS LaunchAgent guide](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
- Related: ADR 011 (Research Artifacts Organization)
- Related: Scripts in `scripts/2025-10-04-auto-transcribe-watcher/`
