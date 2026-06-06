# Active Directory Certificate Services (AD CS) — Abuse and Hardening

## Background

Windows Active Directory is not solely an identity and access management platform — it bundles a significant number of ancillary services, many of which receive far less security scrutiny than core IAM functions. **Active Directory Certificate Services (AD CS)** is one of the most commonly overlooked, and one of the most dangerous when misconfigured.

AD CS is Microsoft's PKI implementation. Because Active Directory already provides a trust anchor for an organization, it can act as an internal Certificate Authority (CA) — issuing certificates to users, machines, and services without requiring internet access to a public CA. Common uses include encrypting file systems, generating and verifying digital signatures, and authenticating users via certificates instead of passwords.

A critical property that makes AD CS particularly dangerous from an attacker's perspective: **certificates survive credential rotation**. If an attacker obtains a certificate for a privileged account and that account's password is subsequently reset, the certificate remains valid until it expires. This makes AD CS a powerful persistence mechanism.

---

## Certificate Templates

Because organizations are too large for administrators to issue every certificate manually, AD CS supports **certificate templates** — pre-configured profiles that define who can request a certificate and what parameters it will have. These templates are where the majority of exploitable misconfigurations occur.

### Enumerating Templates

On any domain-joined machine authenticated to the domain:

```cmd
certutil -v -template > cert_templates.txt
```

This outputs all available templates and their configurations. The output is verbose — the goal is to parse it for the three "toxic" parameter combinations described below.

---

## The Three Exploitable Conditions (ESC1)

For a certificate template to be exploitable for privilege escalation, three conditions must hold simultaneously:

### Condition 1 — Enrollment Permission

The attacker's account (or a group it belongs to) must have either:
- `Allow Enroll` permission on the template, or
- `Allow Full Control` permission

These permissions are typically assigned to AD groups rather than individual users. To check your group memberships:

```cmd
net user YOUR_USERNAME /domain
```

Two groups that commonly have enrollment rights and are worth checking:
- **Domain Users** — any authenticated user can request the certificate
- **Domain Computers** — any machine admin can request a certificate on behalf of that machine

### Condition 2 — Client Authentication EKU

The template must include the **Client Authentication** Extended Key Usage (EKU). This EKU allows the resulting certificate to be used for Kerberos authentication — meaning an attacker can use it to request a TGT as any principal the certificate was issued for.

In the `certutil` output, look for:

```
Client Authentication
```

in the EKU section of each template.

### Condition 3 — Enrollee Supplies Subject (SAN Control)

The template must allow the requester to specify the **Subject Alternative Name (SAN)**. Normally, the CA controls what identity the certificate attests to. If the enrollee can supply the SAN, they can request a certificate that attests to being *any* AD principal — including Domain Admins.

In the `certutil` output, look for:

```
CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT = 1
```

---

## Exploitation Walkthrough

When all three conditions are met, the attack proceeds as follows:

### Step 1 — Request the Certificate via MMC

1. Open `mmc.exe`
2. **File > Add/Remove Snap-in** → add **Certificates**
3. Expand **Personal** → right-click → **All Tasks** → **Request New Certificate**
4. Click through to the **Active Directory Enrollment Policy** dialog
5. Select the vulnerable template — it should show an option to provide additional information

### Step 2 — Configure the Certificate Request

In the certificate request dialog:
- **Subject Name** → Type: `Common Name`, Value: any name (this is cosmetic)
- **Alternative Name** → Type: `User Principal Name`, Value: the UPN of the target privileged account (e.g., a service account or domain admin)

The UPN can be found using AD RSAT tools or PowerView:

```powershell
Get-ADUser -Identity TARGET_USER -Properties UserPrincipalName
```

### Step 3 — Use the Certificate for Kerberos Authentication

After enrolling, use the certificate to request a Kerberos TGT:

```powershell
# Using Rubeus
Rubeus.exe asktgt /user:TARGET_USER /certificate:cert.pfx /password:CERT_PASSWORD /ptt
```

The `/ptt` flag passes the ticket into the current session. With the TGT loaded, the attacker has the full Kerberos privileges of the target account.

### Step 4 — Abuse the Access

With a DA TGT, actions like resetting a domain admin password or performing a DCSync become trivial:

```powershell
# Reset domain admin password
net user Administrator NewPassword123! /domain

# Or perform DCSync with Mimikatz
lsadump::dcsync /user:Administrator
```

---

## Mitigations

| Control | Implementation |
|---------|---------------|
| Audit existing templates | Run `certutil -v -template` and review all templates with `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT = 1` |
| Require CA manager approval | Enable **CA Certificate Manager Approval** on sensitive templates so issuance is gated by a human review |
| Disable SAN override | Remove `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` from templates that don't require it |
| Monitor certificate issuance | Alert on certificate requests where the SAN differs from the requesting account's identity |
| Restrict enrollment permissions | Remove Domain Users/Domain Computers from enrollment ACLs on sensitive templates |

---

## Further Reading

- SpecterOps: *Certified Pre-Owned* — https://posts.specterops.io/certified-pre-owned-d95910965cd2
- Microsoft: Certificate Template Security — https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-security
