# Linux Filesystem Forensics

## Preparation: Using Known-Good Binaries

When investigating a potentially compromised host, system binaries may have been replaced with trojaned versions. Avoid relying on the host's own binaries:

```bash
# Mount an external drive containing known-good tools
mount /dev/sdb1 /mnt/clean

# Prepend the mount point so these binaries take priority
export PATH=/mnt/clean/bin:$PATH
```

---

## High-Risk Directories

These directories are world-writable by default and are commonly used by attackers to stage tools, store payloads, and establish persistence:

| Directory | Why It Matters |
|-----------|---------------|
| `/tmp` | World-writable, cleared on reboot — common staging location |
| `/var/tmp` | World-writable, **persists across reboots** — more durable than `/tmp` |
| `/dev/shm` | Shared memory filesystem, RAM-backed, world-writable — leaves no disk artifact |

```bash
# Find all files owned by a specific group
find / -group GROUPNAME 2>/dev/null

# Find recently modified files in high-risk directories
find /tmp /var/tmp /dev/shm -type f -newer /var/log/syslog 2>/dev/null
```

---

## File Timestamps

Timestamps are among the most valuable artifacts for establishing a timeline of events. On Linux/Unix systems, three timestamps are recorded per file:

### mtime — Modification Time
Records the last time **file contents** were changed.

```bash
ls -l filename          # Shows mtime
stat filename           # Shows all three timestamps
```

### ctime — Change Time
Records the last time **file metadata** was changed (permissions, ownership, filename, link count). Note: ctime is **not** creation time.

```bash
ls -lc filename
```

### atime — Access Time
Records the last time the file was **read**. Note: many systems mount with `noatime` or `relatime` to reduce disk I/O, which affects reliability of this timestamp.

```bash
ls -lu filename
```

### Using `stat` for Full Timestamp View

```bash
stat /etc/passwd
# Output includes:
#   Access: (atime)
#   Modify: (mtime)
#   Change: (ctime)
#   Birth:  (crtime - not always available on Linux)
```

**Timestamp manipulation:** Attackers can modify mtime and atime using `touch -t` but cannot easily forge ctime (it updates automatically on any metadata change). A file with a suspicious mtime that predates the system's install date, or where mtime != ctime, may indicate tampering.

---

## User Account Analysis

### /etc/passwd
Contains all user accounts and their attributes. Format: `username:x:UID:GID:comment:home:shell`

Look for:
- Accounts with UID 0 (root-equivalent) other than `root`
- Accounts with a shell (e.g., `/bin/bash`) that shouldn't have one
- Recently added accounts

```bash
# Find all accounts with UID 0
awk -F: '$3 == 0 {print $1}' /etc/passwd

# Find accounts with interactive shells
awk -F: '$7 !~ /nologin|false/ {print $1, $7}' /etc/passwd
```

### /etc/shadow
Contains password hashes. Requires root to read.

```bash
# Find accounts with no password (empty hash field)
awk -F: '$2 == "" {print $1}' /etc/shadow
```

### Privilege-Escalating Groups

An attacker with a foothold may add their account to high-value groups:

| Group | Risk |
|-------|------|
| `sudo` / `wheel` | Execute commands as root |
| `adm` | Read system log files |
| `shadow` | Read `/etc/shadow` (password hashes) |
| `disk` | Near-unrestricted read access to block devices |

```bash
# Show all groups for a user
groups USERNAME

# Show all members of a group
getent group sudo
getent group shadow
```

All groups and their members are stored in `/etc/group`.

---

## Login and Session History

```bash
# History of logged-in users (reads /var/log/wtmp)
last

# Failed login attempts (reads /var/log/btmp) — requires root
lastb

# Each user's most recent login (reads /var/log/lastlog)
lastlog

# Currently logged-in users
who
w
```

---

## Persistence Mechanisms

### Crontabs
```bash
# Current user's crontab
crontab -l

# All system crontabs
ls -la /etc/cron* /var/spool/cron/crontabs/
```

### Sudoers
```bash
cat /etc/sudoers
ls /etc/sudoers.d/
```

Look for: `NOPASSWD` entries, overly broad `ALL=(ALL)` grants, unusual users with sudo rights.

### SSH Authorized Keys
A public key in `~/.ssh/authorized_keys` grants passwordless SSH access:

```bash
# Check authorized keys for all users with home directories
for user in $(awk -F: '$7 !~ /nologin|false/' /etc/passwd | cut -d: -f1); do
    keyfile="/home/$user/.ssh/authorized_keys"
    [ -f "$keyfile" ] && echo "=== $user ===" && cat "$keyfile"
done

# Also check root
cat /root/.ssh/authorized_keys
```

### Startup Scripts and rc.local
```bash
cat /etc/rc.local
ls /etc/init.d/
ls /etc/systemd/system/        # Systemd services
systemctl list-units --type=service --state=enabled
```

Look for services with unusual names, unexpected binary paths, or services that were recently enabled.

---

## Establishing a Timeline

When reconstructing an intrusion, correlate:

1. **Account creation time** — `stat /home/USERNAME` (ctime of home directory)
2. **File modification times** — `find / -newer /var/log/auth.log -type f 2>/dev/null`
3. **Login events** — `last`, `lastb`, auth log
4. **Command history** — `~/.bash_history`, `~/.zsh_history`
5. **Network connections at time of compromise** — correlate with PCAP or flow data if available

```bash
# Find files modified within a time range
find /var/www /home /tmp -newermt "2024-01-01" ! -newermt "2024-01-02" -type f
```
