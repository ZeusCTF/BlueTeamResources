# THM: Warzone 1

**Category:** Network Forensics / Threat Intelligence  
**Difficulty:** Easy  
**Platform:** TryHackMe  
**Tools:** Brim (Zui), Wireshark, NetworkMiner, VirusTotal, CyberChef

---

## Overview

A packet capture is provided alongside SIEM alert data. The goal is to analyze the traffic, identify the malware family and threat actor, and trace the full attack chain including downloaded payloads and their file destinations on the victim machine.

---

## Methodology

### Task 1 — Alert Signature: Malware C2 Activity

In Brim (now called Zui), search for the alert category:

```
_path=="alert" alert.category=="Malware Command and Control Activity Detected"
```

The alert signature is displayed directly in the `alert.signature` field of the matching event. Copy it verbatim.

---

### Task 2 & 3 — Source and Destination IPs (Defanged)

From the same C2 alert event:
- `src_ip` → source IP (attacker/victim outbound)
- `dest_ip` → destination IP (C2 server)

Defang both IPs using CyberChef's **Defang IP Addresses** operation. Defanging replaces `.` with `[.]` to prevent accidental hyperlinking or resolution.

---

### Task 4 — Most-Detected Domain (VirusTotal Passive DNS)

1. Navigate to [VirusTotal](https://www.virustotal.com)
2. Search tab → enter the destination IP from Task 3
3. Go to **Relations** → **Passive DNS Replication**
4. Sort by detection count — the domain with the highest number of engine detections is the answer
5. Defang this domain for submission

---

### Task 5 & 6 — Threat Group and Malware Family

In VirusTotal, still on the destination IP page:

- **Community** tab → the threat group attribution is listed in community comments/reports → **TA505**
- The malware **family** name is also listed in this section

TA505 is a financially motivated threat actor known for distributing banking trojans and ransomware, including Dridex and Clop.

---

### Task 7 — Majority File Type in Communicating Files

1. In VirusTotal, search for the **domain** from Task 4
2. Navigate to **Relations** → **Communicating Files**
3. Note the predominant file type listed — this reveals what kind of malware commonly communicates with this domain

---

### Task 8 — User-Agent in Network Traffic

Filter Wireshark for HTTP traffic to the flagged C2 IP:

```
http && ip.dst == DEST_IP_HERE
```

Expand any HTTP packet → HTTP layer → `User-Agent` field. Copy the full string.

---

### Task 9 — Additional Associated IPs

In Brim, examine the beginning of the HTTP logs. Two additional IP addresses appear in the early HTTP traffic associated with this attack. These are staging or secondary C2 infrastructure.

```
_path=="http" | sort ts
```

Review the first few entries for IPs beyond the primary C2 — defang both and submit in numerical order.

---

### Task 10 — Downloaded File Names

Open the PCAP in **NetworkMiner** and navigate to the **Files** tab. This tab automatically reconstructs files transferred over the wire from the packet data.

Filter out obviously benign files (images, fonts, etc.). The two **`.msi`** files are the malicious payloads. Their filenames answer this question, in the order corresponding to the IPs from Task 9.

---

### Tasks 11 & 12 — File Save Paths

With the downloaded `.msi` files identified, examine the HTTP traffic for each one in Wireshark:

```
http && http.request.uri contains "FILENAME.msi"
```

Follow the HTTP stream. Within the traffic for each MSI download, there will be data revealing the **full file path** on the victim's system where the files are saved. Two files are written to the same directory for each download.

> **Note:** The answer format requires the same path submitted twice for each question (`C:\path\file1.xyz,C:\path\file2.xyz`). The question wording doesn't make this explicit.

---

## Key Takeaways

- VirusTotal's **Passive DNS** and **Community** tabs are underused — they often directly attribute activity to known threat actors and campaigns
- NetworkMiner's file reconstruction feature is significantly faster than manually extracting files from Wireshark for this type of analysis
- TA505 is a prolific threat actor; familiarity with their TTPs (MSI-based delivery, specific C2 domains) aids faster attribution
- Defanging IPs and domains before sharing them in reports or tickets is a professional habit that prevents accidental exposure
