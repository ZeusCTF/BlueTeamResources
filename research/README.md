# Research Notes

In-depth notes on security topics covering attack techniques, defensive controls, and tooling. Written during independent study and refined through hands-on practice in lab environments and CTF challenges.

---

## Active Directory

| Note | Focus |
|------|-------|
| [AD Certificate Services](./ad-certificate-templates.md) | ESC1 attack path: abusing misconfigured certificate templates for privilege escalation and persistence via forged Kerberos tickets |
| [AD Fundamentals](./active-directory-basics.md) | Domain architecture, Kerberos and NetNTLM authentication internals, GPOs, forest/trust relationships, and hardening guidance |

## Web Application Security

| Note | Focus |
|------|-------|
| [CSRF](./csrf.md) | Attack variants (form, async, Flash, image injection), CSRF token implementation and bypass, SameSite cookie mechanics |
| [SSRF](./ssrf.md) | Loopback and internal network pivoting, cloud metadata endpoint abuse, filter bypass techniques |
| [Insecure Deserialization](./serialization.md) | PHP, Python (pickle), and Java serialization internals; object injection; ysoserial and PHPGGC tooling |

## Digital Forensics & Incident Response

| Note | Focus |
|------|-------|
| [Linux Filesystem Forensics](./linux-fs-forensics.md) | Timestamps (mtime/ctime/atime), persistence mechanisms, user account analysis, timeline reconstruction |
| [Windows Registry Forensics](./windows-registry-forensics.md) | Hive structure and disk locations, persistence keys, user activity artifacts, USB device tracking, execution artifacts |

## Tools & Platforms

| Note | Focus |
|------|-------|
| [Wireshark Reference](./wireshark-reference.md) | Display filter cheat sheet, stream following, statistics views, tshark equivalents |
| [Splunk Reference](./splunk-reference.md) | Roles, search modes, SPL syntax, common security detection searches, knowledge objects |

---

## How These Notes Are Structured

Each note follows a consistent pattern:

1. **Concept explanation** — what it is and why it matters to an attacker or defender
2. **Technical detail** — how it works at the implementation level
3. **Attack/exploitation** — how the technique is applied offensively (where applicable)
4. **Detection and mitigation** — how to identify and remediate the issue

Notes are updated as understanding deepens through practical application.
