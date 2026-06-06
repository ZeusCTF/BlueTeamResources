#!/usr/bin/env bash
# =============================================================================
# mac_persistence_check.sh
#
# Checks common macOS persistence locations for potentially malicious entries.
# Intended as a triage aid — a non-exhaustive first pass to guide further
# investigative effort, not a replacement for a full forensic review.
#
# Usage:
#   chmod +x mac_persistence_check.sh
#   ./mac_persistence_check.sh              # Current user
#   sudo ./mac_persistence_check.sh        # All users + root-owned locations
#
# Tested on: macOS 12 (Monterey), macOS 13 (Ventura), macOS 14 (Sonoma)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No color

section() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
}

info()    { echo -e "  ${GREEN}[+]${NC} $*"; }
warn()    { echo -e "  ${YELLOW}[!]${NC} $*"; }
missing() { echo -e "  ${GREEN}[+]${NC} Not found (expected)"; }

list_dir() {
    local dir="$1"
    if [ -d "$dir" ]; then
        local count
        count=$(ls -A "$dir" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$count" -eq 0 ]; then
            info "$dir — empty"
        else
            warn "$dir — $count item(s):"
            ls -la "$dir" 2>/dev/null | tail -n +2 | sed 's/^/      /'
        fi
    else
        info "$dir — directory does not exist"
    fi
}

# ---------------------------------------------------------------------------
# 1. Launch Agents and Daemons
# ---------------------------------------------------------------------------

section "Launch Agents & Daemons"

echo ""
echo "  System-wide LaunchAgents (all users):"
list_dir "/Library/LaunchAgents"

echo ""
echo "  System-wide LaunchDaemons (root):"
list_dir "/Library/LaunchDaemons"

echo ""
echo "  Current user LaunchAgents (~):"
list_dir "$HOME/Library/LaunchAgents"

echo ""
echo "  Apple-provided LaunchDaemons (reference — should be unmodified):"
info "/System/Library/LaunchDaemons — $(ls /System/Library/LaunchDaemons 2>/dev/null | wc -l | tr -d ' ') items (system-managed)"

# ---------------------------------------------------------------------------
# 2. RunAtLoad key check
# ---------------------------------------------------------------------------

section "Plist Analysis — RunAtLoad Key"

echo ""
echo "  Searching for RunAtLoad=true in /Library/Launch* ..."
if grep -rl "RunAtLoad" /Library/LaunchAgents /Library/LaunchDaemons 2>/dev/null | grep -v '.DS_Store' > /tmp/_runmatch.txt 2>/dev/null && [ -s /tmp/_runmatch.txt ]; then
    warn "Files containing RunAtLoad:"
    while IFS= read -r f; do
        echo "    $f"
        # Extract the actual value to check if it's true or false
        plutil -p "$f" 2>/dev/null | grep -A1 "RunAtLoad" | sed 's/^/      /' || true
    done < /tmp/_runmatch.txt
else
    info "No RunAtLoad keys found in system Launch directories."
fi
rm -f /tmp/_runmatch.txt

if [ -d "$HOME/Library/LaunchAgents" ]; then
    echo ""
    echo "  Searching for RunAtLoad in ~/Library/LaunchAgents ..."
    if grep -rl "RunAtLoad" "$HOME/Library/LaunchAgents" 2>/dev/null > /tmp/_runmatch2.txt 2>/dev/null && [ -s /tmp/_runmatch2.txt ]; then
        warn "Files containing RunAtLoad:"
        while IFS= read -r f; do
            echo "    $f"
            plutil -p "$f" 2>/dev/null | grep -A1 "RunAtLoad" | sed 's/^/      /' || true
        done < /tmp/_runmatch2.txt
    else
        info "No RunAtLoad keys found in ~/Library/LaunchAgents."
    fi
    rm -f /tmp/_runmatch2.txt
fi

# ---------------------------------------------------------------------------
# 3. Crontabs
# ---------------------------------------------------------------------------

section "Crontabs"

echo ""
echo "  Current user crontab:"
if crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' > /tmp/_cron.txt && [ -s /tmp/_cron.txt ]; then
    warn "Crontab entries found:"
    cat /tmp/_cron.txt | sed 's/^/    /'
else
    info "No crontab entries for current user."
fi
rm -f /tmp/_cron.txt

echo ""
echo "  System-wide cron directories:"
for d in /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.monthly /etc/cron.weekly; do
    list_dir "$d"
done

if [ "$(id -u)" -eq 0 ]; then
    echo ""
    echo "  All user crontabs (requires root):"
    if [ -d /private/var/at/tabs ]; then
        local_tabs=$(ls /private/var/at/tabs 2>/dev/null | wc -l | tr -d ' ')
        if [ "$local_tabs" -gt 0 ]; then
            warn "/private/var/at/tabs — $local_tabs file(s):"
            ls -la /private/var/at/tabs | sed 's/^/    /'
        else
            info "/private/var/at/tabs — empty"
        fi
    fi
fi

# ---------------------------------------------------------------------------
# 4. Periodic Scripts
# ---------------------------------------------------------------------------

section "Periodic Scripts"

echo ""
for d in /etc/periodic/daily /etc/periodic/weekly /etc/periodic/monthly; do
    list_dir "$d"
done

# ---------------------------------------------------------------------------
# 5. Dynamic Libraries (Dylib Hijacking / Injection)
# ---------------------------------------------------------------------------

section "Dynamic Libraries"

echo ""
echo "  User library paths:"
list_dir "$HOME/lib"
list_dir "/usr/local/lib"

echo ""
echo "  LD_LIBRARY_PATH / DYLD_INSERT_LIBRARIES environment variables:"
if env | grep -E "LD_LIBRARY_PATH|DYLD_INSERT_LIBRARIES|DYLD_LIBRARY_PATH" > /tmp/_ldenv.txt 2>/dev/null && [ -s /tmp/_ldenv.txt ]; then
    warn "Custom library path variable(s) detected:"
    cat /tmp/_ldenv.txt | sed 's/^/    /'
else
    info "No custom dynamic library path variables found in current environment."
fi
rm -f /tmp/_ldenv.txt

# ---------------------------------------------------------------------------
# 6. Shell Startup Scripts
# ---------------------------------------------------------------------------

section "Shell Startup Scripts"

echo ""
echo "  Checking user home directories for shell startup files:"

USER_DIRS="/Users"
STARTUP_FILES=(".zshrc" ".bashrc" ".bash_profile" ".zprofile" ".profile" ".zshenv")

if [ -d "$USER_DIRS" ]; then
    for user_dir in "$USER_DIRS"/*/; do
        username=$(basename "$user_dir")
        found_any=false
        for startup_file in "${STARTUP_FILES[@]}"; do
            full_path="$user_dir$startup_file"
            if [ -f "$full_path" ]; then
                if [ "$found_any" = false ]; then
                    warn "User: $username"
                    found_any=true
                fi
                echo "    $full_path ($(wc -l < "$full_path" | tr -d ' ') lines)"
            fi
        done
        if [ "$found_any" = false ]; then
            info "User $username — no shell startup scripts found"
        fi
    done
fi

# ---------------------------------------------------------------------------
# 7. Login Items (via plist)
# ---------------------------------------------------------------------------

section "Login Items"

echo ""
UUID=$(ioreg -rd1 -c IOPlatformExpertDevice 2>/dev/null | awk -F'"' '/IOPlatformUUID/{print $4}')
LOGINWINDOW_PLIST="$HOME/Library/Preferences/ByHost/com.apple.loginwindow.$UUID.plist"

if [ -f "$LOGINWINDOW_PLIST" ]; then
    items=$(plutil -p "$LOGINWINDOW_PLIST" 2>/dev/null | grep -c "Path" || true)
    if [ "$items" -gt 0 ]; then
        warn "$items login item(s) found:"
        plutil -p "$LOGINWINDOW_PLIST" 2>/dev/null | sed 's/^/    /'
    else
        info "No login items found in loginwindow plist."
    fi
else
    info "loginwindow plist not found at expected path."
fi

# ---------------------------------------------------------------------------
# 8. Preference Panes (Custom)
# ---------------------------------------------------------------------------

section "Custom Preference Panes"

echo ""
echo "  System-wide preference panes:"
list_dir "/Library/PreferencePanes"

echo ""
echo "  Per-user preference panes:"
if [ -d "$USER_DIRS" ]; then
    for user_dir in "$USER_DIRS"/*/; do
        username=$(basename "$user_dir")
        pane_dir="$user_dir/Library/PreferencePanes"
        if [ -d "$pane_dir" ] && [ "$(ls -A "$pane_dir" 2>/dev/null | wc -l)" -gt 0 ]; then
            warn "User $username has custom preference panes:"
            ls -la "$pane_dir" | tail -n +2 | sed 's/^/    /'
        fi
    done
fi

# ---------------------------------------------------------------------------
# 9. Terminal Startup Commands
# ---------------------------------------------------------------------------

section "Terminal Startup Commands"

echo ""
echo "  Checking Terminal.plist for custom startup commands:"
if [ -d "$USER_DIRS" ]; then
    for user_dir in "$USER_DIRS"/*/; do
        username=$(basename "$user_dir")
        terminal_plist="$user_dir/Library/Preferences/com.apple.Terminal.plist"
        if [ -f "$terminal_plist" ]; then
            cmd=$(plutil -p "$terminal_plist" 2>/dev/null | grep "CommandString" || true)
            if [ -n "$cmd" ]; then
                warn "User $username has a custom Terminal startup command:"
                echo "$cmd" | sed 's/^/    /'
            else
                info "User $username — no custom Terminal startup command"
            fi
        fi
    done
fi

# ---------------------------------------------------------------------------
# 10. Emond Rules (Legacy Persistence)
# ---------------------------------------------------------------------------

section "Emond Rules (Event Monitor Daemon)"

echo ""
echo "  Note: emond was removed in macOS 13 (Ventura)."
list_dir "/etc/emond.d/rules"

# ---------------------------------------------------------------------------
# 11. Folder Action Scripts
# ---------------------------------------------------------------------------

section "Folder Action Scripts"

echo ""
list_dir "/Library/Scripts/Folder Action Scripts"

if [ -d "$HOME/Library/Scripts/Folder Action Scripts" ]; then
    list_dir "$HOME/Library/Scripts/Folder Action Scripts"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

section "Scan Complete"

echo ""
echo "  This script checks common persistence locations."
echo "  Items flagged with ${YELLOW}[!]${NC} warrant further review."
echo ""
echo "  For deeper analysis, consider:"
echo "    - KnockKnock (Objective-See) — https://objective-see.org/products/knockknock.html"
echo "    - BlockBlock (Objective-See) — real-time persistence monitoring"
echo "    - osquery — SQL-based host interrogation"
echo ""
