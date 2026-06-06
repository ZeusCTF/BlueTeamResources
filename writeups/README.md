# Writeups

Challenge writeups from Hack The Box and TryHackMe. Each writeup documents the full methodology — enumeration, exploitation, and post-exploitation — along with key takeaways and defensive recommendations where applicable.

---

## Hack The Box — Sherlocks (Forensics)

| Challenge | Category | Summary |
|-----------|----------|---------|
| [Meerkat](./htb/meerkat.md) | Web / Network Forensics | Bonitasoft BPM brute-force and CVE exploitation; payload staging via pastes.io |
| [Bumblebee](./htb/bumblebee.md) | DFIR / SQLite | phpBB database and access log correlation to reconstruct a forum compromise |
| [Litter](./htb/litter.md) | Network Forensics | DNS tunneling C2 traffic analysis and command extraction |

## TryHackMe

| Room | Category | Summary |
|------|----------|---------|
| [Creative](./thm/creative.md) | Web / PrivEsc | SSRF → internal port scan → SSH key extraction → LD_PRELOAD root |
| [CyberLens](./thm/cyberlens.md) | Web / Windows | Apache Tika 1.17 header injection RCE on a Windows target |
| [Warzone 1](./thm/warzone1.md) | Network Forensics / TI | TA505 malware C2 traffic analysis; NetworkMiner file reconstruction |
| [Warzone 2](./thm/warzone2.md) | Network Forensics / TI | CAB-delivered trojan; full infrastructure mapping across Brim, Wireshark, and VirusTotal |

---

## Tools Used Across Writeups

| Tool | Purpose |
|------|---------|
| Wireshark / tshark | Packet capture analysis |
| Brim (Zui) | SIEM-style log search over PCAPs |
| NetworkMiner | Passive file reconstruction from PCAPs |
| sqlitebrowser | SQLite database browsing |
| Nmap / RustScan | Port scanning and service enumeration |
| Gobuster | Directory and virtual host brute-forcing |
| Metasploit | Exploit framework |
| Burp Suite | HTTP interception and manipulation |
| VirusTotal | File, URL, and IP threat intelligence |
| CyberChef | Data encoding, decoding, and defanging |
| John the Ripper | Password and key cracking |
