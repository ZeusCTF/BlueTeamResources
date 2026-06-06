# Active Directory — Architecture, Authentication, and Hardening

## Core Concepts

A **Windows domain** is a collection of users and computers under centralized administration via **Active Directory (AD)**. The server running AD services is called a **Domain Controller (DC)**. The benefits of this model are:

- Centralized identity management across all machines in the domain
- Uniform security policy enforcement via Group Policy
- Delegated administration without requiring local admin access everywhere

---

## Object Types

### Users
User objects represent both human employees and **service accounts** (e.g., an account a database service runs under). All are considered **security principals** — they can be assigned permissions to resources on the network.

### Machines
When a computer joins a domain, a machine object is created for it. Machine accounts (named `COMPUTERNAME$`) are also security principals. They have limited domain-wide permissions but are typically local administrators on their assigned machine.

### Security Groups
Groups are security principals whose permissions are inherited by members. Both users and machines can be members, and groups can be nested. Key built-in groups include:

| Group | Default Privileges |
|-------|-------------------|
| Domain Admins | Full control over the domain |
| Server Operators | Manage domain servers |
| Backup Operators | Bypass file permissions for backup purposes |
| Domain Users | Default group for all user accounts |

### Organizational Units (OUs)
OUs are containers used to organize users and machines, primarily for the purpose of applying Group Policy Objects. Key distinction: **OUs are for policy application; Security Groups are for permissions**.

---

## Authentication Protocols

### Kerberos (Modern Default)

Kerberos uses a ticket-based system. The **Key Distribution Center (KDC)**, running on the Domain Controller, issues tickets.

**Full authentication flow:**

1. **TGT Request:** The client sends its username and an encrypted timestamp to the KDC. The KDC returns a **Ticket Granting Ticket (TGT)** and a **Session Key**, both encrypted so only the client can use them.

2. **TGS Request:** When the client wants to access a specific service, it presents the TGT to the KDC along with the **Service Principal Name (SPN)** of the target service. The KDC returns a **Ticket Granting Service (TGS)** ticket, encrypted with the service account's password hash.

3. **Service Access:** The client presents the TGS to the service. The service decrypts it with its own password hash, validates the embedded Session Key, and grants access.

**Why this matters for attackers:**
- **Kerberoasting:** Any authenticated user can request a TGS for any service. The TGS is encrypted with the service account's hash — meaning it can be taken offline and cracked. Services running as highly privileged accounts with weak passwords are the primary target.
- **Pass-the-Ticket:** Stolen TGTs or TGSs can be injected into sessions to impersonate users.
- **Golden/Silver Tickets:** Forged tickets crafted with stolen key material (KRBTGT hash for Golden, service account hash for Silver).

### NetNTLM (Legacy Compatibility)

NetNTLM uses a challenge-response mechanism and does not require a KDC:

1. Client sends an authentication request to the target server
2. Server generates a random **challenge** and sends it to the client
3. Client combines its NTLM hash with the challenge to produce a **response**
4. Server forwards both challenge and response to the DC for verification
5. DC recalculates the expected response and compares — if they match, access is granted

**Why this matters for attackers:**
- **NTLM Relay:** An attacker positioned as a man-in-the-middle can relay captured NetNTLM authentication attempts to other services, potentially gaining unauthorized access without cracking the hash
- **Pass-the-Hash:** NTLM hashes captured from memory (e.g., via Mimikatz) can be used directly for authentication without knowing the plaintext password

---

## Group Policy Objects (GPOs)

GPOs define configuration baselines applied to users and computers within OUs. They are managed via the **Group Policy Management** tool and distributed to domain members via a network share called **SYSVOL** on the DC.

Key operational notes:
- GPOs apply to the linked OU and all child OUs by default
- **Security Filtering** allows GPOs to be scoped to specific users or groups within an OU
- Changes can take time to propagate; force an immediate sync with `gpupdate /force`
- The **Settings** tab of a GPO shows exactly what configurations it enforces

---

## Forest and Trust Relationships

**Trees** are collections of domains sharing a namespace (e.g., `thm.local`, `sub1.thm.local`, `sub2.thm.local`).

**Forests** are collections of trees with different namespaces — typically the result of mergers or acquisitions.

**Trust relationships** control whether users in one domain can access resources in another:

| Trust Type | Description |
|------------|-------------|
| One-way | Domain A trusts Domain B → B's users can access A's resources |
| Two-way | Mutual trust; default when joining a tree |
| Transitive | Trust extends through the chain (A trusts B, B trusts C → A trusts C) |

**Enterprise Admins** is a special group that grants administrative privileges across all domains in a forest — significantly broader than Domain Admins.

---

## Hardening Guidance

### Credential Storage
Windows stores password hashes in two formats: **LM** (weak, legacy, susceptible to fast brute-force) and **NT** (stronger). LM hashes should be disabled via Group Policy where not required for legacy compatibility.

### Network Protocol Hardening

**SMB Signing:** Enables integrity verification of SMB traffic, protecting against MITM and relay attacks. Configure via Group Policy.

**LDAP Signing:** Forces the DC to only accept signed LDAP requests, protecting against replay and injection attacks. Configure via Group Policy.

### Account Model
Follow a **least-privilege** approach with tiered account types:

| Tier | Account Type | Used For |
|------|-------------|----------|
| Tier 0 | Domain Admins, Enterprise Admins | DC administration only |
| Tier 1 | Server admins | Server administration only |
| Tier 2 | Workstation admins | Endpoint administration |

Tier 0 accounts should never be used interactively on lower-tier systems — doing so exposes credentials to potential extraction.

### Common Attack Mitigations

| Attack | Mitigation |
|--------|-----------|
| Kerberoasting | Use strong, randomly generated service account passwords (>25 chars); audit SPNs; use Group Managed Service Accounts (gMSA) |
| Credential brute-force via RDP | Never expose RDP to the internet; implement account lockout policies; use MFA |
| Weak credentials | Enforce strong password policies via Group Policy; consider passphrases |
| NTLM relay | Enable SMB signing; disable NTLM where possible; use EPA for LDAP |

### Tooling
Microsoft's **Security Compliance Toolkit (MSCT)** provides pre-built security baselines and a **Policy Analyzer** tool for comparing GPO configurations and identifying inconsistencies.
