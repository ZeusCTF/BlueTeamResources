# Tools

Scripts and utilities built during CTF and independent security research. Each tool solves a problem encountered in practice.

---

## virustotal_lookup.py

A CLI wrapper around the VirusTotal API v3 for quick lookups during triage without leaving the terminal.

### Features
- URL, IP address, and file hash lookups
- Visual detection count output (bar chart in terminal)
- File upload fallback when a hash is not found in the VT database
- API key via environment variable (`VT_API_KEY`), CLI flag, or prompt
- Interactive REPL mode for multiple lookups in one session

### Setup

```bash
pip install requests
export VT_API_KEY="your_key_here"   # Optional — tool will prompt if not set
```

A free API key is available at https://www.virustotal.com/gui/join-us (4 lookups/minute, 500/day).

### Usage

```bash
# Single lookups
python virustotal_lookup.py --url https://suspicious-domain.com/payload
python virustotal_lookup.py --ip 185.220.101.45
python virustotal_lookup.py --hash d41d8cd98f00b204e9800998ecf8427e

# Interactive mode (multiple lookups without re-running)
python virustotal_lookup.py --interactive

# Pass API key directly (skips env variable and prompt)
python virustotal_lookup.py --key YOUR_KEY --ip 1.2.3.4
```

### Example Output

```
[*] Looking up IP: 185.220.101.45

[*] Analysis results:
  malicious       47  ███████████████████████████████████████████████
  suspicious       3  ███
  undetected      17  █████████████████
  harmless         8  ████████
  timeout          0

[*] WHOIS information:
  NetRange: 185.220.100.0 - 185.220.103.255
  OrgName:  Tor Project
  ...
```

---

## mac_persistence_check.sh

A triage script for macOS that checks common persistence locations and flags anything present for follow-up review.

### What It Checks

| Category | Locations |
|----------|-----------|
| Launch Agents/Daemons | `/Library/Launch*`, `~/Library/LaunchAgents` |
| RunAtLoad keys | All plist files in Launch directories |
| Crontabs | Current user + system cron directories |
| Periodic scripts | `/etc/periodic/daily`, `/weekly`, `/monthly` |
| Dynamic libraries | `~/lib`, `/usr/local/lib`, `DYLD_INSERT_LIBRARIES` env var |
| Shell startup scripts | `.zshrc`, `.bashrc`, `.bash_profile`, `.zprofile`, `.profile` |
| Login items | `com.apple.loginwindow` plist |
| Preference panes | `/Library/PreferencePanes` and per-user |
| Terminal startup commands | `com.apple.Terminal.plist` |
| Emond rules | `/etc/emond.d/rules` (macOS ≤12) |
| Folder action scripts | `/Library/Scripts/Folder Action Scripts` |

### Usage

```bash
chmod +x mac_persistence_check.sh

# Current user context
./mac_persistence_check.sh

# Full scan including all users and root-owned directories
sudo ./mac_persistence_check.sh
```

Output is color-coded: green `[+]` for expected/empty locations, yellow `[!]` for anything present that warrants review.

### Limitations

- Not a replacement for dedicated tools like KnockKnock (Objective-See)
- Some locations require root access to read (run with `sudo` for full coverage)
- Does not parse or analyze plist file contents beyond the `RunAtLoad` key check

---

## plist_tool.py

A utility for reading, editing, and converting macOS `.plist` files. Handles binary, XML, and JSON plist formats transparently.

### Features
- View all key-value pairs with type information
- Search for a specific key (with case-insensitive fallback)
- Add or update keys
- Convert between binary, XML, and JSON formats
- Both CLI (scriptable) and interactive REPL modes

### Usage

```bash
# CLI mode — scriptable, good for automation
python plist_tool.py com.apple.Terminal.plist --view
python plist_tool.py com.apple.Terminal.plist --keys
python plist_tool.py com.apple.Terminal.plist --search RunAtLoad
python plist_tool.py com.apple.Terminal.plist --set MyKey "MyValue"
python plist_tool.py com.apple.Terminal.plist --convert xml

# Interactive mode — good for exploration
python plist_tool.py com.apple.Terminal.plist
```

### Notes on Plist Formats

```bash
# Identify plist format
file something.plist
# "Apple binary property list" → binary
# "XML 1.0 document text"     → XML

# Manual conversion via plutil (macOS built-in)
plutil -convert xml1 something.plist     # → XML
plutil -convert binary1 something.plist  # → binary
plutil -convert json something.plist     # → JSON
```

---

## requirements.txt

```
requests>=2.28.0
```

Install with:
```bash
pip install -r requirements.txt
```
