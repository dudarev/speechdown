#!/usr/bin/env zsh

# SpeechDown Watchdog Uninstall Script
# Removes the watchdog cron job

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WATCHDOG_SCRIPT="$SCRIPT_DIR/watchdog.sh"

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

# Check if cron entry exists
if ! crontab -l 2>/dev/null | grep -F "$WATCHDOG_SCRIPT" > /dev/null; then
    print_info "Watchdog cron job is not installed"
    exit 0
fi

# Remove from crontab
crontab -l 2>/dev/null | grep -vF "$WATCHDOG_SCRIPT" | crontab -
print_success "Removed watchdog from crontab"

echo ""
print_info "Watchdog log file preserved: ~/logs/speechdown_watchdog.log"
echo "  To remove: rm ~/logs/speechdown_watchdog.log"
