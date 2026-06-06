# HTB Sherlock: Bumblebee

**Category:** Forensics / DFIR  
**Difficulty:** Easy  
**Files Provided:** `phpbb.sqlite3`, `access.log`

---

## Overview

We are given a SQLite database belonging to a phpBB forum installation and an accompanying web server access log. The goal is to reconstruct an intrusion: identify the attacker, determine what they accessed, and establish a precise timeline.

---

## Tools Used

- `sqlitebrowser` — GUI for browsing SQLite databases
- `grep` — log filtering
- `date` — timestamp conversion

---

## Methodology

### Step 1 — Open the Database

```bash
sqlitebrowser phpbb.sqlite3
```

The first table worth examining is **`phpbb_users`**. It contains usernames, email addresses, registration IPs, and last-login IPs in the `user_ip` column.

**Task 1 & 2 — Attacker IP:** Sorting by `user_ip` and looking for public (non-RFC1918) addresses identifies the attacker's IP. This same IP answers both the "who registered the malicious account" and "what IP performed the attack" questions.

---

### Step 2 — Correlate Posts to the Attacker IP

With the attacker's IP identified, navigate to the **`phpbb_posts`** table and filter on `poster_ip` matching that address.

**Task 3:** The `post_ip` column in the matching rows gives the IP used when the attacker made their posts — confirming active forum participation from the same address.

---

### Step 3 — Find the Malicious Link

Still in `phpbb_posts`, one post contains a link to an `update.php` file. The key detail is that this URL **does not appear in `access.log`** — meaning it was posted but never accessed through the server's web interface, suggesting it was planted for social engineering purposes rather than direct exploitation.

**Task 4:** The `update.php` URL found in the posts table is the answer.

---

### Step 4 — Find the Initial Admin Login Attempt

This step required correlating the database and access log. The login attempt table in the database was empty, so I turned to `access.log`.

```bash
# 'login' alone returns too many irrelevant results
grep 'login' access.log

# Filtering for admin-specific assets narrows it down significantly
grep 'admin' access.log
```

The `/adm/style/admin.js?assets_version=4` path appears only when an admin panel is loaded — this stylesheet is served exclusively to authenticated admin sessions. The **first timestamp** this path appears in the log is the answer.

**Timestamp format required:** Convert the Apache log format to the answer format:

```bash
# Apache format: [19/Apr/2023:12:34:56 +0000]
# Convert as needed to match expected submission format
```

---

### Step 5 — Recover the Admin Password

Navigate to the **`phpbb_config`** table in the database. This table stores application configuration key-value pairs — and in this case, also contains the admin password in plaintext (or recoverable form).

**Task 6:** The password value stored in `phpbb_config` is the answer.

---

### Step 6 — Identify the Admin's User Agent

From **`phpbb_users`**, retrieve the `user_ip` for the admin account. Then grep `access.log` for that IP to find all requests made by that address:

```bash
grep "ADMIN_IP_HERE" access.log
```

The User-Agent string appears in every log line — copy it from any of the admin's requests.

---

### Step 7 — Find the Group Modification

```bash
grep -i 'group' access.log
```

A POST request for group modification appears in the results. The timestamp of this request is the answer to Task 8 (same format as Task 5).

---

### Step 8 — Find the SQL Injection Attempt

```bash
grep -i 'sql' access.log
```

An SQL injection attempt appears in the log. The same request's byte size (the final numeric field in each Apache log line) answers Task 10.

---

## Timeline Reconstruction

| Event | Source | Detail |
|-------|--------|--------|
| Attacker account registration | `phpbb_users.user_ip` | Public IP identified |
| Malicious post with update.php link | `phpbb_posts` | URL not in access log |
| First admin panel access | `access.log` | `/adm/style/admin.js` |
| Group privilege modification | `access.log` | POST to group endpoint |
| SQL injection attempt | `access.log` | Malicious query in URL |

---

## Key Takeaways

- SQLite databases for web applications are rich forensic artifacts — posts, users, configs, and login attempts are all stored in queryable tables
- When a login attempt table is empty, shift to access logs and look for admin-only assets (stylesheets, JS files only served to authenticated admin sessions) as a proxy for login events
- Correlating IP addresses across the database and access logs is the core technique for reconstructing web application intrusions
- Always check `phpbb_config` (and equivalent config tables in other CMSes) — misconfigured or debug installations sometimes store credentials there
