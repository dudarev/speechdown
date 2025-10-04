#!/usr/bin/env zsh

# SpeechDown Watchdog Cron Setup Script
# Installs a cron job to monitor the file watcher service

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WATCHDOG_SCRIPT="$SCRIPT_DIR/watchdog.sh"
CRON_INTERVAL="${1:-*/15}"  # Default: every 15 minutes

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Make watchdog script executable
chmod +x "$WATCHDOG_SCRIPT"
print_success "Made watchdog script executable"

# Create cron entry
CRON_COMMAND="$CRON_INTERVAL * * * * $WATCHDOG_SCRIPT"

# Check if cron entry already exists
if crontab -l 2>/dev/null | grep -F "$WATCHDOG_SCRIPT" > /dev/null; then
    print_info "Watchdog cron job already exists"
    echo ""
    echo "Current cron jobs:"
    crontab -l | grep -F "$WATCHDOG_SCRIPT"
    exit 0
fi

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
print_success "Added watchdog to crontab"

echo ""
echo "Watchdog Monitoring Installed"
echo "=============================="
echo ""
echo "The watchdog will check every 15 minutes if the watcher is running."
echo "If the watcher is down, it will automatically restart it."
echo ""
echo "Configuration:"
echo "  Check interval: Every 15 minutes"
echo "  Watchdog log:   ~/logs/speechdown_watchdog.log"
echo "  Cron entry:     $CRON_COMMAND"
echo ""
echo "Useful commands:"
echo "  View cron jobs:      crontab -l"
echo "  View watchdog logs:  tail -f ~/logs/speechdown_watchdog.log"
echo "  Remove watchdog:     $SCRIPT_DIR/uninstall_watchdog.sh"
echo ""
print_info "Note: The watchdog only logs when it detects issues or takes action"
