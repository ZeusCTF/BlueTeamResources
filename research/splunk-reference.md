# Splunk Reference

## Roles

Three default roles exist in Splunk, each with progressively broader permissions:

| Role | Capabilities |
|------|-------------|
| **User** | Can only see their own knowledge objects and those explicitly shared with them |
| **Power** | Can create and share knowledge objects with other app users; can run real-time searches |
| **Admin** | Can install apps, ingest data, create and manage all knowledge objects |

---

## Data Summary Concepts

On the **Data Summary** tab, three fields categorize ingested data:

| Field | Meaning |
|-------|---------|
| **Sourcetypes** | The classification of data — defines how Splunk parses and formats events (e.g., `access_combined`, `WinEventLog:Security`) |
| **Sources** | The origin of data — a file path, network port, or API endpoint that is sending data into Splunk |
| **Hosts** | The machine or device the data originated from |

---

## Search Modes

Three search modes control the tradeoff between speed and data richness:

| Mode | Behavior |
|------|----------|
| **Fast** | Reduces field discovery to improve performance; only returns event data and fields necessary for the search |
| **Smart** | Adapts based on the search type — behaves like Fast for transforming searches, like Verbose for event searches |
| **Verbose** | Returns all event data and fields possible; slowest but most complete |

For investigative work, **Verbose** is generally preferable. For dashboard searches and scheduled reports, **Fast** reduces load.

---

## Search Results

When a search is run, Splunk returns **events** — individual log entries matching the query. Key behaviors:

- Results are returned in **reverse chronological order** (newest first)
- Matching search terms are **highlighted** in the event text
- Timestamps are normalized internally to a consistent format; the timestamp displayed to you is rendered in your account's configured timezone

---

## Search Processing Language (SPL) Basics

### Time Range
Always specify a time range — unbounded searches across large datasets are slow and may time out. Use the time picker or inline:

```spl
earliest=-24h latest=now
earliest="01/01/2024:00:00:00" latest="01/02/2024:00:00:00"
```

### Basic Search Syntax
```spl
index=main sourcetype=access_combined status=404
```

### Field Filtering
```spl
index=windows EventCode=4625
| fields src_ip, user, EventCode, _time
```

### Filtering Results
```spl
index=main
| where status > 400
| search uri="*/admin*"
```

### Deduplication
```spl
index=main src_ip=*
| dedup src_ip
```

### Counting and Grouping
```spl
index=main sourcetype=access_combined
| stats count by src_ip
| sort -count
```

```spl
index=main
| stats count by user, src_ip, EventCode
| where count > 10
```

### Top Values
```spl
index=main
| top limit=20 src_ip
```

### Time-Based Aggregation
```spl
index=main
| timechart span=1h count by src_ip
```

### String Operations
```spl
index=main
| eval user=lower(user)
| search user="*admin*"
```

### Rex (Regex Extraction)
```spl
index=main sourcetype=syslog
| rex field=_raw "Failed password for (?P<username>\S+) from (?P<src_ip>\d+\.\d+\.\d+\.\d+)"
| table _time, username, src_ip
```

---

## Common Security Searches

### Brute-Force Detection — Failed Logins
```spl
index=windows EventCode=4625
| stats count by src_ip, TargetUserName
| where count > 20
| sort -count
```

### Successful Login After Multiple Failures
```spl
index=windows (EventCode=4625 OR EventCode=4624)
| stats count(eval(EventCode=4625)) as failures,
        count(eval(EventCode=4624)) as successes by src_ip, TargetUserName
| where failures > 10 AND successes > 0
```

### Detecting New Admin Account Creation
```spl
index=windows EventCode=4720
| table _time, SubjectUserName, TargetUserName, src_ip
```

### PowerShell Execution Logging
```spl
index=windows sourcetype="WinEventLog:Microsoft-Windows-PowerShell/Operational"
| search ScriptBlockText="*Invoke-*" OR ScriptBlockText="*-EncodedCommand*" OR ScriptBlockText="*DownloadString*"
| table _time, ComputerName, ScriptBlockText
```

### Large Data Transfers (Potential Exfiltration)
```spl
index=network
| stats sum(bytes_out) as total_bytes by src_ip, dest_ip
| where total_bytes > 100000000
| eval total_mb=round(total_bytes/1024/1024, 2)
| sort -total_mb
```

---

## Knowledge Objects

Knowledge objects enrich, normalize, and classify data within Splunk. Key types:

| Object | Purpose |
|--------|---------|
| **Field Extractions** | Parse custom fields from raw event text using regex or delimiters |
| **Lookups** | Enrich events with external reference data (e.g., map IP → hostname, user → department) |
| **Saved Searches** | Store and schedule frequently run searches |
| **Alerts** | Trigger actions (email, webhook, ticket) when a search returns results |
| **Dashboards** | Visualize search results with charts, tables, and maps |
| **Tags** | Apply human-readable labels to field-value pairs |
| **Event Types** | Classify events matching a search as a named type |

---

## Practical Tips

- Use `index=*` sparingly — always scope to the relevant index to reduce search time
- The `_raw` field contains the original unprocessed log line — useful for regex extraction
- `_time` is always available and is Splunk's normalized timestamp field
- `| head 100` limits results during exploratory searches to avoid loading too much data
- Save frequently-used filters as **Saved Searches** to avoid retyping and ensure consistency
- When building alerts, test the underlying search thoroughly first to minimize false positives
