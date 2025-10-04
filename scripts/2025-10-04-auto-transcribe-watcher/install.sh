#!/usr/bin/env zsh

# SpeechDown Auto-Transcribe Watcher Installation Script
# Installs the file watcher as a macOS LaunchAgent

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_TEMPLATE="$SCRIPT_DIR/com.speechdown.watcher.plist.template"
PLIST_NAME="com.speechdown.watcher.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"
WATCHER_SCRIPT="$SCRIPT_DIR/watcher.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    if ! command -v fswatch &> /dev/null; then
        print_error "fswatch is not installed"
        echo "Install it with: brew install fswatch"
        exit 1
    fi
    print_success "fswatch is installed"
    
    if ! command -v sd &> /dev/null; then
        print_error "sd is not installed or not in PATH"
        exit 1
    fi
    print_success "sd is installed"
    
    if [[ ! -f "$WATCHER_SCRIPT" ]]; then
        print_error "Watcher script not found: $WATCHER_SCRIPT"
        exit 1
    fi
    print_success "Watcher script found"
    
    if [[ ! -f "$PLIST_TEMPLATE" ]]; then
        print_error "LaunchAgent template not found: $PLIST_TEMPLATE"
        exit 1
    fi
    print_success "LaunchAgent template found"
}

# Prompt for configuration
get_configuration() {
    echo ""
    echo "=== Configuration ==="
    
    # Watch directory
    read "watch_dir?Enter directory to watch [default: $HOME/Downloads]: "
    WATCH_DIR="${watch_dir:-$HOME/Downloads}"
    
    if [[ ! -d "$WATCH_DIR" ]]; then
        print_error "Directory does not exist: $WATCH_DIR"
        exit 1
    fi
    
    # Log directory
    LOG_DIR="$HOME/logs"
    mkdir -p "$LOG_DIR"
    LOG_FILE="$LOG_DIR/speechdown_watcher.log"
    LOCK_FILE="$HOME/speechdown_watcher.lock"
    STDOUT_LOG="$LOG_DIR/speechdown_watcher-stdout.log"
    STDERR_LOG="$LOG_DIR/speechdown_watcher-stderr.log"
    
    # Speechdown command path
    SPEECHDOWN_CMD="$(which sd)"
    
    # PATH environment variable
    PATH_VAR="$PATH"
    
    echo ""
    print_info "Configuration:"
    echo "  Watch directory: $WATCH_DIR"
    echo "  Log file: $LOG_FILE"
    echo "  Speechdown command: $SPEECHDOWN_CMD"
}

# Create and install LaunchAgent
install_launch_agent() {
    print_info "Installing LaunchAgent..."
    
    # Make watcher script executable
    chmod +x "$WATCHER_SCRIPT"
    print_success "Made watcher script executable"
    
    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "$LAUNCH_AGENTS_DIR"
    
    # Generate plist from template
    sed -e "s|SCRIPT_PATH_PLACEHOLDER|$WATCHER_SCRIPT|g" \
        -e "s|WATCH_DIR_PLACEHOLDER|$WATCH_DIR|g" \
        -e "s|LOG_FILE_PLACEHOLDER|$LOG_FILE|g" \
        -e "s|LOCK_FILE_PLACEHOLDER|$LOCK_FILE|g" \
        -e "s|SPEECHDOWN_CMD_PLACEHOLDER|$SPEECHDOWN_CMD|g" \
        -e "s|PATH_PLACEHOLDER|$PATH_VAR|g" \
        -e "s|STDOUT_LOG_PLACEHOLDER|$STDOUT_LOG|g" \
        -e "s|STDERR_LOG_PLACEHOLDER|$STDERR_LOG|g" \
        "$PLIST_TEMPLATE" > "$PLIST_PATH"
    
    print_success "Created LaunchAgent plist: $PLIST_PATH"
    
    # Load the LaunchAgent
    launchctl load "$PLIST_PATH"
    print_success "Loaded LaunchAgent"
}

# Main installation
main() {
    echo "SpeechDown Auto-Transcribe Watcher Installation"
    echo "================================================"
    echo ""
    
    check_prerequisites
    get_configuration
    
    echo ""
    read "confirm?Proceed with installation? [y/N]: "
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi
    
    install_launch_agent
    
    echo ""
    print_success "Installation complete!"
    echo ""
    echo "✨ The watcher is now running!"
    echo ""
    echo "🚀 AUTO-START ENABLED:"
    echo "   The watcher will automatically start when your system boots."
    echo "   No manual action needed after restarts - it just works!"
    echo ""
    echo "📁 Watching: $WATCH_DIR"
    echo "📝 Logs:     $LOG_FILE"
    echo ""
    echo "Useful commands:"
    echo "  View logs:           tail -f $LOG_FILE"
    echo "  Check status:        launchctl list | grep speechdown"
    echo "  Stop watcher:        launchctl unload $PLIST_PATH"
    echo "  Start watcher:       launchctl load $PLIST_PATH"
    echo "  Restart watcher:     launchctl unload $PLIST_PATH && launchctl load $PLIST_PATH"
    echo "  Uninstall:           $SCRIPT_DIR/uninstall.sh"
    echo ""
    print_info "To test: Copy an audio file (.m4a, .mp3, etc.) to $WATCH_DIR"
}

main
