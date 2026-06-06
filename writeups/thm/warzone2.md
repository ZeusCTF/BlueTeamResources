# THM: Warzone 2

**Category:** Network Forensics / Threat Intelligence  
**Difficulty:** Easy  
**Platform:** TryHackMe  
**Tools:** Brim (Zui), Wireshark, VirusTotal, CyberChef, NetworkMiner

---

## Overview

A follow-up to Warzone 1. Another packet capture with SIEM alerts is provided. The investigation focuses on identifying a network trojan, tracing a malicious file download through a CAB archive, and mapping associated malicious infrastructure.

---

## Methodology

### Task 1 — Alert Signature: Network Trojan Detected

In Brim, search for the relevant alert category:

```
_path=="alert" alert.category=="A Network Trojan was Detected"
```

The `alert.signature` field in the matching event contains the answer. Copy it verbatim.

---

### Task 2 — Alert Signature: Corporate Privacy Violation

Same approach, different search term:

```
_path=="alert" alert.category=="Potential Corporate Privacy Violation"
```

Copy the signature from the matching event.

---

### Task 3 — Triggering IP (Defanged)

Both alerts above share the same source IP (`src_ip`). Copy it, paste into CyberChef, apply **Defang IP Addresses**, and submit.

---

### Task 4 — Full URI of the Malicious Download (Defanged)

In Wireshark, filter for HTTP traffic to the destination IP from the alerts:

```
http && ip.dst == DEST_IP_HERE
```

Locate the HTTP GET request for the malicious file. The full URI combines:
- The `Host` header value (hostname)
- The request path (`http.request.uri`)

Concatenate them (`hostname + path`), then defang the result using CyberChef's **Defang URL** operation.

---

### Task 5 — Payload Name Inside the CAB File

Export the HTTP object (the `.cab` file) from Wireshark:

```
File > Export Objects > HTTP
```

Generate an MD5 hash of the exported file:

```bash
md5sum exported_file.cab
```

Search this hash on VirusTotal. Navigate to the **Details** tab — the file names of contents extracted from the archive are listed there, revealing the payload name embedded in the CAB.

---

### Task 6 — User-Agent

Still on the same HTTP packet from Task 4, expand the HTTP section in Wireshark and copy the `User-Agent` header value.

---

### Task 7 — Additional Malicious Domains

Review the DNS queries and HTTP hostnames throughout the full PCAP in Brim:

```
_path=="dns" | count() by query | sort -r count
```

Cross-reference domains against VirusTotal. Two domains (beyond the primary C2) are flagged as malicious. Submit them defanged and in alphabetical order.

> The question mentions "other domains" — focus on domains that appear in the traffic and return malicious verdicts in VirusTotal, excluding the one already identified in Task 4.

---

### Task 8 — IPs Flagged as "Not Suspicious Traffic"

In Brim, search for the `Not Suspicious Traffic` classification:

```
_path=="notice" note=="Not Suspicious Traffic"
```

Two IP addresses appear in the results. Defang both and submit in numerical order.

---

### Task 9 — Malicious Domains for First "Not Suspicious" IP

Take the first IP from Task 8 and filter all traffic involving it:

```
_path=="http" id.resp_h==FIRST_IP_HERE
```

Note all unique domain names (hostnames) that appear in requests to this IP. Cross-reference each against VirusTotal — several will be flagged as malicious. Submit them defanged and in alphabetical order.

---

### Task 10 — Domain for Second "Not Suspicious" IP

Repeat the same process for the second IP from Task 8:

```
_path=="http" id.resp_h==SECOND_IP_HERE
```

Only one malicious domain is associated with this IP.

---

## Full Infrastructure Map

| Role | Indicator | Type |
|------|-----------|------|
| Primary C2 | See Task 3 IP | IP |
| Malicious download host | See Task 4 URI | URL |
| Secondary infrastructure | See Tasks 9/10 | Domains |

---

## Key Takeaways

- CAB files are a classic Windows malware delivery mechanism — they bypass some email filters and allow payload bundling
- VirusTotal's **Details** tab for archive files lists extracted filenames, making it easy to identify payloads without extracting locally
- "Not Suspicious Traffic" classifications in IDS/SIEM alerts can be misleading — always verify flagged IPs against external threat intel regardless of internal classification
- Building a complete infrastructure map (IPs, domains, URIs) across both Warzone challenges demonstrates how threat actors use layered infrastructure to complicate attribution and takedown
