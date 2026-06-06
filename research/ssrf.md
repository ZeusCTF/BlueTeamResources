# Server-Side Request Forgery (SSRF)

## What Is It?

SSRF is a vulnerability where user-controlled input is used to construct a server-side HTTP request without sufficient validation. The attacker doesn't make the request themselves — they cause the vulnerable server to make it on their behalf. This is significant because requests originating from the server often have access to resources the attacker cannot reach directly: internal services, cloud metadata endpoints, and backend infrastructure.

---

## Basic SSRF — Same Server

The simplest case: an application fetches a URL supplied by the user and returns the response.

**Example — vulnerable parameter:**
```
https://example.com/fetch?url=https://external-site.com/data
```

An attacker tests whether the server will fetch its own loopback address:
```
https://example.com/fetch?url=http://127.0.0.1/
https://example.com/fetch?url=http://localhost/admin
```

If the application returns content, the attacker can enumerate internal paths:
```
http://127.0.0.1/config
http://127.0.0.1/admin/users
http://127.0.0.1/.env
```

This is particularly impactful if the server's internal web interface lacks authentication (assuming it's not reachable from outside) or exposes administrative functionality.

---

## Internal Network SSRF — Pivoting to Backend Services

More complex environments use multiple servers — a front-end web server communicates with back-end databases, internal APIs, or microservices hosted on private IP ranges (RFC1918: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`). These internal services are intentionally not exposed to the internet.

An attacker can supply internal addresses in the vulnerable parameter to reach these services through the web application:

```
https://example.com/fetch?url=http://192.168.1.50:8080/internal-api/users
https://example.com/fetch?url=http://10.0.0.5:3306/  # MySQL
```

### Internal Port Scanning via SSRF

By iterating over ports on a known internal IP, an attacker can enumerate what services are running on internal hosts:

```python
# Conceptual - iterating via Burp Intruder or a custom script
for port in range(1, 65536):
    url = f"http://192.168.1.50:{port}/"
    # Differences in response time, status code, or body indicate open ports
```

Response behavior differences (timeout vs. connection refused vs. actual response) reveal which ports are open.

---

## Cloud Metadata Endpoint Abuse

In cloud environments (AWS, GCP, Azure), every instance has access to a metadata service at a well-known internal address. These services return instance configuration, IAM role credentials, and other sensitive data — and they only require network access from the instance itself (no authentication).

**AWS IMDSv1 (legacy):**
```
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE_NAME
```

A successful SSRF request to this endpoint returns temporary AWS credentials (access key, secret key, session token) that can be used to interact with AWS APIs with the permissions of the instance's IAM role.

**Mitigations in cloud environments:**
- **IMDSv2 (AWS):** Requires a session-oriented PUT request before GET requests — not forgeable via simple SSRF
- Restrict IAM role permissions to the minimum required (least privilege)
- Monitor metadata API access in CloudTrail

---

## Common SSRF Bypass Techniques

Applications sometimes attempt to block SSRF by blocklisting `localhost`, `127.0.0.1`, or RFC1918 ranges. These filters are often bypassable:

| Bypass | Mechanism |
|--------|-----------|
| `http://127.1/` | Shorthand notation for `127.0.0.1` |
| `http://2130706433/` | Decimal representation of `127.0.0.1` |
| `http://0x7f000001/` | Hex representation of `127.0.0.1` |
| `http://[::1]/` | IPv6 loopback |
| DNS rebinding | Domain resolves to external IP initially, then resolves to internal IP after validation |
| Open redirects | Chain with an open redirect on a trusted domain |

---

## Impact

SSRF severity depends on what the internal network contains:

| Internal Service Reached | Potential Impact |
|--------------------------|-----------------|
| Internal admin panels | Unauthenticated admin access |
| Cloud metadata service | Credential theft, full cloud account compromise |
| Internal databases (direct) | Data exfiltration |
| Internal APIs | Business logic abuse, data access |
| Other internal web apps | Lateral movement |

---

## Mitigations

- **Allowlist valid URL schemes and destinations** — if only HTTPS requests to specific external domains are needed, enforce exactly that
- **Deny RFC1918 and loopback addresses** at the network level (not just application level — application-level filters are too easily bypassed)
- **Segment internal networks** — internal services should not be reachable from the web application server unless explicitly required
- **Use IMDSv2** in AWS environments
- **Validate and sanitize all user-supplied URLs** — reject unexpected schemes (`file://`, `gopher://`, `dict://`)
