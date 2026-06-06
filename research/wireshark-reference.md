# Wireshark Reference

## Interface Overview

When a packet is selected in the packet list, two panes populate:
- **Packet Details** — hierarchical breakdown of protocol layers
- **Packet Bytes** — raw hex/ASCII representation; hovering over a field in Packet Details highlights the corresponding bytes here

### Protocol Layer Structure
Most packets contain the following layers in the Details pane:

| Layer | Protocol | OSI Layer |
|-------|----------|-----------|
| Frame | Frame metadata | 1 |
| Ethernet | Source/destination MAC | 2 |
| Internet Protocol | Source/destination IP | 3 |
| Transport | TCP/UDP/ICMP | 4 |
| Application | HTTP, DNS, TLS, etc. | 5 (not always present) |

Packets without an application-layer protocol listed in the protocol column will typically not have a Layer 5 entry in the Details pane.

---

## Navigation

| Action | Method |
|--------|--------|
| Go to specific packet number | `Ctrl+G` or Go > Go to Packet |
| Find packet by content | `Ctrl+F` or Edit > Find Packet (supports string, hex, regex) |
| Mark a packet | Right-click > Mark/Unmark (marks do not persist across sessions) |
| Add a comment | Edit > Packet Comment |
| Adjust timestamp format | View > Time Display Format |

---

## Exporting Data

```
File > Export Objects > HTTP    # Reconstruct files transferred over HTTP
File > Export Objects > SMB     # Reconstruct files transferred over SMB
File > Export Specified Packets # Export a filtered subset of packets
```

---

## Display Filter Reference

Display filters narrow what packets are shown without discarding others from the capture.

### Filtering by IP

```wireshark
ip.addr == 192.168.1.1          # Any packet involving this IP
ip.src == 192.168.1.1           # Packets from this IP
ip.dst == 192.168.1.1           # Packets to this IP
ip.src != 192.168.1.1           # Exclude packets from this IP
ip.addr == 192.168.1.0/24       # Entire subnet
```

### Filtering by Protocol

```wireshark
http                            # HTTP traffic
dns                             # DNS traffic
tcp                             # All TCP
udp                             # All UDP
!(dns or arp or udp)            # Exclude noise protocols
http or dns                     # Show HTTP and DNS
```

### Filtering by Port

```wireshark
tcp.port == 443                 # TCP port 443 (either direction)
tcp.dstport == 8080             # Packets going TO port 8080
tcp.srcport == 4444             # Packets originating FROM port 4444
udp.port == 53                  # DNS (UDP 53)
```

### Filtering HTTP

```wireshark
http.request                    # HTTP requests only
http.response                   # HTTP responses only
http.request.method == "POST"   # POST requests
http.response.code == 200       # Successful responses
http.request.uri contains "login"  # Requests to URLs containing "login"
http.host == "example.com"      # Requests to a specific host
```

### Combining Filters

```wireshark
ip.dst == 10.0.0.5 && http      # HTTP traffic to a specific IP
http && !ip.src == 192.168.1.1  # HTTP excluding a source IP
tcp.dstport == 443 || tcp.dstport == 80   # HTTPS or HTTP
```

---

## Logical Operator Reference

Wireshark supports two equivalent syntaxes:

| Meaning | Symbol | Word |
|---------|--------|------|
| Equal | `==` | `eq` |
| Not equal | `!=` | `ne` |
| Greater than | `>` | `gt` |
| Less than | `<` | `lt` |
| AND | `&&` | `and` |
| OR | `\|\|` | `or` |
| XOR | `^^` | `xor` |
| NOT | `!` | `not` |

---

## Follow Stream

Right-click any TCP/UDP/HTTP packet → **Follow > TCP Stream** (or HTTP Stream) to reconstruct the full conversation between two endpoints in a human-readable format. Extremely useful for:
- Reconstructing HTTP sessions (see exactly what was sent/received)
- Reading plaintext protocol data
- Identifying C2 traffic patterns

---

## Statistics Useful for Triage

```
Statistics > Protocol Hierarchy    # Volume breakdown by protocol — good for spotting anomalies
Statistics > Conversations         # Top talkers; sort by bytes to find data exfiltration
Statistics > Endpoints             # All IPs/MACs seen; useful for identifying unknown hosts
Statistics > IO Graph              # Traffic volume over time; spikes may indicate attacks
Statistics > HTTP > Requests       # All HTTP request URIs in one view
```

---

## Useful `tshark` Commands (CLI Equivalent)

```bash
# Extract all HTTP request URIs
tshark -r capture.pcap -Y "http.request" -T fields -e http.host -e http.request.uri

# Extract DNS query names
tshark -r capture.pcap -Y "dns.flags.response == 0" -T fields -e dns.qry.name

# Count packets per destination IP
tshark -r capture.pcap -T fields -e ip.dst | sort | uniq -c | sort -rn

# Extract files transferred over HTTP
tshark -r capture.pcap --export-objects http,/output/directory/

# Filter for specific IP and save to new pcap
tshark -r capture.pcap -Y "ip.addr == 10.0.0.5" -w filtered.pcap
```
