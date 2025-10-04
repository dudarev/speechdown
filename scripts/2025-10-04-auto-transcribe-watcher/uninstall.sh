#!/usr/bin/env zsh

# SpeechDown Auto-Transcribe Watcher Uninstallation Script

set -euo pipefail

PLIST_NAME="com.speechdown.watcher.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

main() {
    echo "SpeechDown Auto-Transcribe Watcher Uninstallation"
    echo "=================================================="
    echo ""
    
    if [[ ! -f "$PLIST_PATH" ]]; then
        print_info "LaunchAgent is not installed"
        exit 0
    fi
    
    read "confirm?Are you sure you want to uninstall the watcher? [y/N]: "
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "Uninstallation cancelled"
        exit 0
    fi
    
    # Unload the LaunchAgent
    if launchctl list | grep -q "com.speechdown.watcher"; then
        launchctl unload "$PLIST_PATH"
        print_success "Unloaded LaunchAgent"
    else
        print_info "LaunchAgent was not running"
    fi
    
    # Remove plist file
    rm "$PLIST_PATH"
    print_success "Removed LaunchAgent plist"
    
    echo ""
    print_success "Uninstallation complete!"
    echo ""
    print_info "Log files in ~/logs/ and the lock file (if present) were not removed"
    echo "  To remove logs: rm -f ~/logs/speechdown_watcher*.log"
    echo "  To remove lock: rm -f ~/speechdown_watcher.lock"
}

main
