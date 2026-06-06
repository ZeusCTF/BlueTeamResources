# Cross-Site Request Forgery (CSRF)

## What Is It?

CSRF is a vulnerability where an attacker tricks a victim's browser into making an unwanted request to a site where the victim is already authenticated. Because browsers automatically include cookies with requests to a given origin, the target site cannot distinguish the forged request from a legitimate one.

The attacker never needs to see the response — many useful actions (money transfers, password changes, account modifications) don't require reading the reply.

---

## Attack Phases

A successful CSRF attack requires three conditions to be true simultaneously:

1. **The attacker understands the target request format.** They must know how the web application structures the state-changing request they want to forge — the URL, method, and parameters.

2. **The victim has an active authenticated session.** The victim must already be logged in to the target site, with a valid session cookie present in the browser.

3. **The application lacks CSRF defenses.** The application cannot differentiate the forged request from a legitimate one — meaning it's not validating a CSRF token, not checking the `Origin`/`Referer` header, or not using SameSite cookies correctly.

---

## Attack Variants

### Classic Form-Based CSRF

The most common form. The attacker hosts an HTML page with a form that auto-submits to the target:

```html
<form action="https://bank.example.com/transfer" method="POST">
  <input type="hidden" name="to" value="attacker_account">
  <input type="hidden" name="amount" value="10000">
</form>
<script>document.forms[0].submit();</script>
```

When the victim loads the attacker's page, the form submits silently. The victim's browser includes their session cookie automatically — the bank sees a request that looks entirely legitimate.

### Asynchronous (XHR/Fetch) CSRF

Some modern applications use `XMLHttpRequest` or `fetch()` for state-changing operations instead of form submissions. CSRF via these mechanisms works identically in principle — the attacker crafts JavaScript that sends the appropriate request — but the same-origin policy restricts reading cross-origin responses. Crucially, it does **not** prevent the request itself from being sent, only the response from being read. For actions where only the side effect matters (not the response), XHR-based CSRF is viable.

### Flash-Based CSRF (Legacy)

Adobe Flash (now defunct) had vulnerabilities that enabled cross-origin request forgery via malicious `.swf` files. Relevant only in environments with legacy Flash components still running.

### Hidden Image/Link Injection

An attacker embeds a 1x1 transparent pixel with a `src` pointing to a state-changing GET endpoint:

```html
<img src="https://target.com/delete-account?confirm=true" width="1" height="1">
```

This only works against applications that use GET requests for state-changing actions — itself a violation of HTTP semantics, but unfortunately common.

---

## Defenses

### CSRF Tokens (Most Common)

A unique, unpredictable, session-bound value is embedded in every form and validated server-side on submission.

**Double Submit Cookie pattern:**
1. On login, the server generates a random token and sets it both as a cookie and as a hidden form field
2. On form submission, both values are sent — the cookie automatically (by the browser) and the form field explicitly (by the page)
3. The server checks that both values match

An attacker on a different origin cannot read the cookie value (same-origin policy) and therefore cannot forge a matching form field value.

**Vulnerabilities in CSRF token implementations:**
- Tokens not tied to the session (any valid token works for any user)
- Predictable token generation (sequential IDs, timestamps)
- Token transmitted in the URL (logged in server access logs, leaked in Referer header)
- XSS vulnerability on the same origin can read tokens from the DOM

### SameSite Cookies

The `SameSite` cookie attribute instructs the browser when to include a cookie in cross-site requests:

| Value | Behavior | CSRF Protection |
|-------|----------|----------------|
| `Strict` | Cookie only sent with same-site requests | Strong — no cookie on any cross-origin request |
| `Lax` | Cookie sent with same-site requests and top-level navigations using safe methods (GET) | Moderate — POST-based CSRF blocked; GET-based attacks still possible |
| `None` | Cookie sent with all requests | None — must be paired with `Secure` attribute |

`SameSite=Lax` is the browser default in modern Chrome/Firefox and provides meaningful protection for most CSRF scenarios. `SameSite=Strict` provides the strongest protection but may break legitimate cross-site navigation flows (e.g., following a link from an email into an authenticated session).

### Other Controls

- **`Origin` / `Referer` header validation:** Reject requests where the header indicates a cross-origin source. Not foolproof (headers can be omitted) but useful as defense-in-depth.
- **Re-authentication for sensitive actions:** Require the user to re-enter their password for high-impact actions (account deletion, password change, large transfers).
- **Custom request headers:** APIs using `fetch()` can require a custom header (e.g., `X-Requested-With: XMLHttpRequest`) — cross-origin requests cannot set custom headers without a CORS preflight, which the server can reject.

---

## Why CSRF Tokens Can Still Fail

Even a correctly implemented CSRF token scheme can be bypassed under certain conditions:

| Bypass Scenario | Mechanism |
|----------------|-----------|
| XSS on same origin | JavaScript can read the CSRF token from the DOM and include it in a forged request |
| Same-origin policy misconfiguration | If CORS is overly permissive (`Access-Control-Allow-Origin: *`), cross-origin reads become possible |
| Subdomain cookie injection | An attacker with control of a subdomain can inject cookies, potentially overwriting a CSRF cookie |
| Predictable tokens | Tokens generated from weak randomness can be guessed |
| MITM (HTTP) | Tokens transmitted over unencrypted HTTP can be intercepted |
