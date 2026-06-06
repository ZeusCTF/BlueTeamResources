# Security Portfolio

A collection of CTF writeups, security research notes, and tooling built while working through platforms like Hack The Box, TryHackMe, and independent study.

---

## Navigation

| Directory | Contents |
|-----------|----------|
| [`/writeups`](./writeups/) | HTB Sherlock and THM challenge writeups |
| [`/research`](./research/) | Deep-dive notes on security topics |
| [`/tools`](./tools/) | Scripts and utilities built during practice |
| [`/labs`](./labs/) | Lab setup guides and environment notes |

---

## Highlighted Writeups

- **[HTB Sherlock: Meerkat](./writeups/htb/meerkat.md)** — Bonitasoft CVE exploitation and attacker persistence via pastes.io; covers HTTP stream analysis and MITRE ATT&CK mapping
- **[HTB Sherlock: Bumblebee](./writeups/htb/bumblebee.md)** — SQLite forensics on a phpBB database; correlating access logs with DB records to reconstruct an intrusion
- **[HTB Sherlock: Litter](./writeups/htb/litter.md)** — DNS-based C2 traffic analysis in Wireshark
- **[THM: Creative](./writeups/thm/creative.md)** — SSRF to internal port discovery, SSH key extraction, and LD_PRELOAD privilege escalation
- **[THM: CyberLens](./writeups/thm/cyberlens.md)** — Apache Tika RCE via header injection on a Windows target

---

## Research Notes

- **[Active Directory Certificate Services (AD CS)](./research/ad-certificate-templates.md)** — Abusing certificate templates for privilege escalation and persistence; ESC1 attack path walkthrough
- **[Active Directory Fundamentals](./research/active-directory-basics.md)** — Domain structure, Kerberos/NetNTLM auth, GPOs, and hardening guidance
- **[CSRF](./research/csrf.md)** — Attack phases, async and Flash-based variants, SameSite cookies, and token bypass techniques
- **[SSRF](./research/ssrf.md)** — Basic and multi-server exploitation patterns
- **[Insecure Deserialization](./research/serialization.md)** — PHP/Python serialization internals, object injection, and exploitation tooling
- **[Linux Filesystem Forensics](./research/linux-fs-forensics.md)** — Timestamps, persistence locations, and user account analysis
- **[Windows Registry Forensics](./research/windows-registry-forensics.md)** — Key hives, autorun locations, USB artifacts, and shellbags
- **[Wireshark Reference](./research/wireshark-reference.md)** — Filter cheat sheet and packet analysis workflow
- **[Splunk Reference](./research/splunk-reference.md)** — Roles, search modes, and SPL basics

---

## Tools

| Tool | Language | Description |
|------|----------|-------------|
| [`virustotal_lookup.py`](./tools/virustotal_lookup.py) | Python | CLI tool for VirusTotal URL, IP, and file hash lookups with upload fallback |
| [`mac_persistence_check.sh`](./tools/mac_persistence_check.sh) | Bash | macOS persistence artifact checker covering LaunchAgents, cron, dylibs, and more |
| [`plist_tool.py`](./tools/plist_tool.py) | Python | View, edit, search, and convert macOS plist files (binary/XML/JSON) |

---

## Platforms & Certifications

- **Hack The Box** — Active participant; Sherlock (forensics) track focus
- **TryHackMe** — Active participant

---

## Setup

No dependencies are required to browse this repository. To run the Python tools:

```bash
pip install requests
python tools/virustotal_lookup.py --help
```

For the macOS persistence checker:

```bash
chmod +x tools/mac_persistence_check.sh
./tools/mac_persistence_check.sh
```
