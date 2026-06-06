# Home Lab Setup Guide

A practical guide to building a local security lab for practicing offensive and defensive techniques without relying entirely on external platforms like HTB or THM.

---

## Why a Local Lab?

External platforms are excellent for structured learning but have constraints: challenges are pre-built, the environment resets, and you can't freely modify infrastructure. A local lab allows you to:

- Deliberately misconfigure services to understand how they fail
- Practice detection engineering by generating known-malicious traffic and tuning rules
- Test tools and exploits in a controlled environment before applying them on challenge platforms
- Build and break Active Directory environments at will

---

## Hardware Requirements

A dedicated machine is ideal but not required. A modern laptop with 16GB RAM can comfortably run 3–4 VMs simultaneously.

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 16 GB | 32 GB |
| Storage | 256 GB SSD | 500 GB+ SSD |
| CPU | 4 cores | 8+ cores with VT-x/AMD-V |

---

## Hypervisor Options

| Hypervisor | Platform | Cost | Notes |
|------------|----------|------|-------|
| VirtualBox | Windows/macOS/Linux | Free | Good starting point; limited performance |
| VMware Workstation Pro | Windows/Linux | Free (as of 2024) | Better performance and snapshot management than VirtualBox |
| VMware Fusion Pro | macOS | Free (as of 2024) | Best option for macOS hosts |
| Proxmox VE | Bare metal Linux | Free | Best for a dedicated lab machine; web UI; supports clustering |

---

## Core VM Images

### Attacker Machine
**Kali Linux** is the standard choice. Download the pre-built VM image (saves setup time):
- https://www.kali.org/get-kali/#kali-virtual-machines

Alternatively, **Parrot OS Security Edition** is lighter on resources.

### Vulnerable Target Machines
Purpose-built vulnerable VMs for practice:

| Image | Focus Area | Source |
|-------|-----------|--------|
| Metasploitable 2/3 | General exploitation | Rapid7 |
| DVWA (Docker) | Web application attacks | GitHub |
| VulnHub machines | Varied | vulnhub.com |
| Windows Evaluation VMs | Windows/AD attacks | Microsoft |

### Windows Evaluation VMs
Microsoft provides free 90-day evaluation licenses for Windows Server and Windows 10/11 Enterprise:
- https://www.microsoft.com/en-us/evalcenter/

These are essential for practicing Active Directory attacks.

---

## Network Architecture

Isolate your lab from your home network. The goal is to prevent accidental exposure of vulnerable VMs to the internet or your home devices.

### Recommended Setup

```
[Home Router]
      |
[Host Machine]
      |
  [VMware/VirtualBox]
      |
  [Host-Only or NAT Network]  ←── All lab VMs live here
      |
  ┌───────────────────────────────────┐
  │  Kali (attacker)   10.10.10.10   │
  │  Win Server 2019   10.10.10.20   │
  │  Win 10 Client     10.10.10.30   │
  │  Ubuntu Target     10.10.10.40   │
  └───────────────────────────────────┘
```

**Network mode options:**
- **Host-Only** — VMs can talk to each other and the host, but not the internet. Best for isolated AD labs.
- **NAT** — VMs share the host's internet connection. Needed for downloading tools inside VMs, but exposes VMs to less isolation.
- **Internal Network** — VMs can only talk to each other, not the host or internet. Maximum isolation.

A common pattern is to use NAT for initial setup (so VMs can download packages), then switch to Host-Only for attack practice.

---

## Building a Basic Active Directory Lab

A minimal AD lab for practicing attacks like Kerberoasting, AS-REP Roasting, and AD CS abuse requires:

1. **Windows Server 2019/2022** — Domain Controller
2. **Windows 10/11** — Domain-joined workstation (simulates a user machine)
3. **Kali Linux** — Attacker machine

### Domain Controller Setup (Abbreviated)

```powershell
# On Windows Server — install AD DS role
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools

# Promote to Domain Controller
Install-ADDSForest `
  -DomainName "lab.local" `
  -DomainNetBiosName "LAB" `
  -ForestMode "WinThreshold" `
  -DomainMode "WinThreshold" `
  -InstallDns `
  -Force

# After reboot — create a standard user and a service account
New-ADUser -Name "Alice Smith" -SamAccountName "asmith" -AccountPassword (ConvertTo-SecureString "Password123!" -AsPlainText -Force) -Enabled $true
New-ADUser -Name "svc_sql" -SamAccountName "svc_sql" -AccountPassword (ConvertTo-SecureString "Sqlservice1!" -AsPlainText -Force) -Enabled $true

# Set an SPN on the service account (makes it Kerberoastable)
Set-ADUser svc_sql -ServicePrincipalNames @{Add="MSSQLSvc/sql.lab.local:1433"}
```

### Join Workstation to Domain

On the Windows 10 VM:
1. Set DNS to point to the Domain Controller's IP
2. System Properties → Change → Domain → `lab.local`
3. Log in with domain admin credentials when prompted

### Deliberately Misconfigure for Practice

```powershell
# Create a Kerberoastable account (SPN + weak password)
# Already done above with svc_sql

# Create an AS-REP Roastable account (no pre-auth required)
Set-ADAccountControl -Identity "asmith" -DoesNotRequirePreAuth $true

# Add a user to a high-privilege group for lateral movement practice
Add-ADGroupMember -Identity "Domain Admins" -Members "asmith"
```

---

## Recommended Tools to Install on Kali

```bash
# Update first
sudo apt update && sudo apt upgrade -y

# AD-focused tools (most are pre-installed on Kali)
sudo apt install -y bloodhound neo4j crackmapexec impacket-scripts \
                    evil-winrm kerbrute ldap-utils

# Download Rubeus (pre-compiled) for Kerberos attacks
# https://github.com/r3motecontrol/Ghostpack-CompiledBinaries

# Install BloodHound
sudo neo4j start
bloodhound &
# Default neo4j creds: neo4j / neo4j (change on first login)
```

---

## Capturing Your Own Traffic for Analysis Practice

Generate traffic between your lab VMs, then capture it with Wireshark or tcpdump for analysis practice.

```bash
# Capture on Kali while performing an attack
sudo tcpdump -i eth0 -w /tmp/lab_capture.pcap

# Or use tshark
sudo tshark -i eth0 -w /tmp/lab_capture.pcap

# Stop with Ctrl+C, then open in Wireshark
wireshark /tmp/lab_capture.pcap
```

Useful traffic to capture:
- Kerberos authentication (domain login, TGT/TGS requests)
- LDAP queries (BloodHound enumeration)
- SMB traffic (lateral movement, file transfers)
- DNS (normal vs. tunneled comparison)

---

## Snapshot Strategy

Snapshots let you reset a VM to a known-good state without reinstalling. Use them aggressively.

```
[Base Install]           ← Take snapshot here after OS install + tools
      |
[Domain Configured]      ← Take snapshot here after AD setup
      |
[Misconfigured]          ← Take snapshot here after adding vulnerable configs
      |
[Post-Exploitation]      ← Optional: snapshot mid-attack to resume later
```

In VMware: VM menu → Take Snapshot. In VirtualBox: Machine → Take Snapshot.

---

## Further Resources

| Resource | URL |
|----------|-----|
| TCM Security Free AD Lab Guide | https://academy.tcm-sec.com |
| VulnHub (free vulnerable VMs) | https://www.vulnhub.com |
| LOLBAS (Living off the Land) | https://lolbas-project.github.io |
| GTFOBins (Linux privesc) | https://gtfobins.github.io |
| HackTricks (technique reference) | https://book.hacktricks.xyz |
| Impacket (Python AD toolkit) | https://github.com/fortra/impacket |
