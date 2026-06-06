# HTB Sherlock: Meerkat

**Category:** Forensics / Threat Hunting  
**Difficulty:** Easy  
**Files Provided:** `meerkat.pcap`, `meerkat-alerts.json`

---

## Overview

A company believes their new self-hosted IT ticketing system may have been compromised. We are provided a packet capture and a JSON alert file and asked to determine what happened, how, and what the attacker left behind.

---

## Methodology

### Step 1 — Triage the Alert File

The first thing I did was open `meerkat-alerts.json`. The raw output was a single block, so I copied it and used a JSON formatter to make it readable.

The alert data pointed toward HTTP-based activity against a `/bonita` path, which is characteristic of **Bonitasoft** — an open-source Business Process Management (BPM) platform.

```bash
# Pretty-print the JSON for easier reading
cat meerkat-alerts.json | python3 -m json.tool > meerkat-alerts-pretty.json
```

Searching the JSON for the `/bonita` path quickly surfaced the relevant CVE.

---

### Step 2 — Identify the CMS and CVE

The `/bonita` URI path in both the JSON alerts and the HTTP packets in the PCAP confirmed the target was **Bonitasoft BPM**.

Cross-referencing the behavior (unauthenticated access attempts followed by exploitation) with public vulnerability databases identified the relevant CVE. The attack pattern matched a known authentication bypass and RCE vulnerability in older Bonitasoft versions.

---

### Step 3 — Identify the Attack Type

Opening the PCAP in Wireshark and filtering for HTTP traffic:

```
http.request
```

Scrolling through the requests, a large volume of POST requests to `/bonita/loginservice` were visible in rapid succession — a clear indicator of a **credential brute-force attack**.

Additionally, several requests had the string `i18ntranslation` appended to the path, which is the specific string associated with the exploit for this CVE.

---

### Step 4 — Count Brute-Force Attempts

To count unique usernames tried during the brute-force:

```bash
tshark -r meerkat.pcap -Y "http.request.method == POST" -T fields -e http.file_data \
  | grep -oP 'username=[^&]+' \
  | sort -u \
  | wc -l
```

This approach extracts the `username` field from each POST body, deduplicates, and counts. The result gives the number of distinct usernames attempted.

---

### Step 5 — Identify the Successful Account

Continuing to trace the HTTP stream, after the brute-force phase the attacker's requests shift — POST requests start returning successful responses rather than auth failures, and subsequent requests are made in the context of a specific user session.

Examining these successful requests identified **`seb.broom`** as the account whose credentials were successfully brute-forced. Subsequent HTTP activity (file downloads, command execution) all occurred under this session.

---

### Step 6 — Trace the Exploitation

After gaining access, the attacker leveraged the Bonitasoft CVE to execute commands on the server. The exploitation involved:

1. Using the `i18ntranslation` path to bypass authentication controls
2. Issuing commands through the application that caused the server to download and execute remote content

The remote content was hosted on **`pastes.io`** — a paste site used to stage the payload. This was visible in the HTTP stream as outbound GET requests from the server to pastes.io URLs.

---

### Step 7 — Identify the Payload File and Persistence Mechanism

The pastes.io URL in the HTTP stream contained the filename of the downloaded script directly in the path.

The script, once downloaded, was written to a specific file on the server — this file path is the **persistence mechanism**, as it ensured the attacker could maintain access after initial exploitation.

---

### Step 8 — MITRE ATT&CK Mapping

| Tactic | Technique | ID |
|--------|-----------|-----|
| Initial Access | Exploit Public-Facing Application | T1190 |
| Credential Access | Brute Force | T1110 |
| Execution | Command and Scripting Interpreter | T1059 |
| Persistence | Server Software Component | T1505 |
| Command & Control | Web Service (paste site staging) | T1102 |

---

## Key Takeaways

- JSON alert files are often the fastest triage starting point; the PCAP provides the supporting detail
- The `/bonita` path is a strong indicator of Bonitasoft deployments and associated CVEs
- Paste sites (pastes.io, pastebin.com, etc.) are commonly used for payload staging because they bypass domain reputation filters
- Brute-force attacks against web application login endpoints are detectable by volume of POST requests to authentication endpoints in a short time window
