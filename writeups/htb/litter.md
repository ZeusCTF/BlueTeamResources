# HTB Sherlock: Litter

**Category:** Forensics / Network Analysis  
**Difficulty:** Easy  
**Files Provided:** `litter.pcap`

---

## Overview

A packet capture has been flagged for review. We need to identify the suspicious protocol, the attacker's infrastructure, and reconstruct the commands sent through the covert channel.

---

## Tools Used

- Wireshark
- `tshark`

---

## Methodology

### Step 1 — Protocol Identification (Task 1)

Opening the PCAP in Wireshark and reviewing the protocol distribution (Statistics > Protocol Hierarchy), one protocol stands out in terms of volume relative to what would be expected on a normal network: **DNS**.

A high volume of DNS queries — especially to unusual or randomly-generated subdomains — is a classic indicator of **DNS tunneling**, a technique used to exfiltrate data or receive C2 commands by encoding information within DNS query and response fields.

```
# Wireshark filter to isolate DNS traffic
dns
```

Reviewing the DNS queries confirmed the suspicion: queries were being made to abnormally long or encoded subdomains, consistent with data being encoded in the DNS query names themselves.

---

### Step 2 — Identify the Suspect Host (Task 2)

Sorting the PCAP by the most frequently appearing IP addresses (Statistics > Conversations, or sorting the packet list by source/destination) reveals one external IP address that is the destination for the overwhelming majority of the anomalous DNS traffic.

```bash
# Count DNS conversations by destination IP
tshark -r litter.pcap -Y "dns" -T fields -e ip.dst | sort | uniq -c | sort -rn | head
```

The most prevalent external IP is the C2 server address.

---

### Step 3 — Extract Attacker Commands (Task 3)

With DNS tunneling confirmed, the commands sent by the attacker are encoded within the DNS query names. To extract them:

```bash
# Extract all DNS query names
tshark -r litter.pcap -Y "dns.flags.response == 0" -T fields -e dns.qry.name
```

DNS tunneling tools typically encode data in the subdomain portion of queries (the part before the registered domain). Stripping the base domain and base64-decoding (or applying whatever encoding scheme the tool uses) the subdomain labels reveals the plaintext commands.

Examining the earliest DNS queries in the capture gives the **first command** sent by the attacker to the compromised host.

---

## Key Takeaways

- DNS is a commonly overlooked protocol in network monitoring because it is necessary for almost all internet activity — this makes it an attractive covert channel
- DNS tunneling indicators include: high query volume, abnormally long subdomains, queries to a single external resolver (rather than the organization's DNS server), and low TTL values
- `tshark` with field extraction (`-T fields -e dns.qry.name`) is faster than Wireshark for bulk DNS analysis
- DNS filtering/monitoring at the perimeter (e.g., DNS RPZ, Pi-hole, or commercial DNS security products) is an effective control against this technique

---

## Detection Opportunities

| Indicator | Detection Method |
|-----------|-----------------|
| High DNS query volume per host | SIEM threshold alert |
| Long subdomain labels (>50 chars) | DNS query length monitoring |
| Single external resolver receiving all queries | DNS traffic baselining |
| Low-entropy vs high-entropy query ratio | Statistical analysis / ML |
