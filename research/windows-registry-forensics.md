# Windows Registry Forensics

## Registry Structure

The Windows Registry is a hierarchical database that stores configuration for the OS, hardware, installed software, and user preferences. It is organized into **root keys** (hives), each storing a specific category of information:

| Root Key | Abbreviation | Contents |
|----------|-------------|----------|
| `HKEY_CURRENT_USER` | HKCU | Configuration for the currently logged-on user |
| `HKEY_USERS` | HKU | All loaded user profiles (HKCU is a subkey of this) |
| `HKEY_LOCAL_MACHINE` | HKLM | Machine-wide configuration (all users) |
| `HKEY_CLASSES_ROOT` | HKCR | File associations and COM registration (merged view of HKLM\Software\Classes and HKCU\Software\Classes) |
| `HKEY_CURRENT_CONFIG` | HKCC | Hardware profile in use at boot |

---

## Hive File Locations on Disk

Registry hives are stored as files and can be examined offline (e.g., from a forensic image):

| Hive | Path |
|------|------|
| SYSTEM | `C:\Windows\System32\Config\SYSTEM` |
| SOFTWARE | `C:\Windows\System32\Config\SOFTWARE` |
| SECURITY | `C:\Windows\System32\Config\SECURITY` |
| SAM | `C:\Windows\System32\Config\SAM` |
| NTUSER.DAT | `C:\Users\USERNAME\NTUSER.DAT` |
| USRCLASS.DAT | `C:\Users\USERNAME\AppData\Local\Microsoft\Windows\UsrClass.dat` |
| Amcache | `C:\Windows\AppCompat\Programs\Amcache.hve` |

**Backups:** Registry hive backups live at `C:\Windows\System32\Config\RegBack`. Comparing the backup against the live hive can reveal recent changes.

**Transaction logs:** Each hive location also has `.LOG` files containing pending transactions not yet committed to the hive — relevant for examining very recent changes.

---

## System Information

```
SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName
→ Machine hostname

SYSTEM\CurrentControlSet\Control\TimeZoneInformation
→ System time zone

SOFTWARE\Microsoft\Windows NT\CurrentVersion
→ OS version, build number, install date

SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces
→ Network interface configuration (IP addresses, DNS servers)
```

### Control Sets

The `SYSTEM` hive contains **ControlSet001** and **ControlSet002**:
- `ControlSet001` — the control set the machine booted with
- `ControlSet002` — the last known good configuration

The **volatile** `CurrentControlSet` is created at runtime and is the most current. On a live system it maps to the active control set; when examining an offline image, check:

```
SYSTEM\Select\Current   → value indicates which ControlSet is the current one
```

---

## Persistence Locations

These registry keys execute programs at user logon or system startup:

```
NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Run
NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\RunOnce
SOFTWARE\Microsoft\Windows\CurrentVersion\Run
SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
SOFTWARE\Microsoft\Windows\CurrentVersion\policies\Explorer\Run
```

Malware frequently uses `Run` keys to achieve persistence. Look for:
- Entries pointing to unusual directories (`%TEMP%`, `%APPDATA%`, `C:\Users\Public`)
- Obfuscated command lines (PowerShell `-EncodedCommand`, `cmd /c`)
- Recently added entries (correlate timestamps with the suspected compromise window)

---

## User Activity Artifacts

### Recently Opened Documents
```
NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs
```

Organized by file extension. Shows the most recently opened files per type.

### File Open/Save Dialog History
```
NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePIDlMRU
NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU
```

Records the paths used in Windows file open/save dialogs. Useful for proving a user navigated to a specific directory.

### Windows Search History
```
NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths
NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery
```

Typed paths in Explorer's address bar and search terms entered in the Start Menu.

### Shellbags
Shellbags record that a folder was **opened in Windows Explorer** — even if the folder no longer exists. This is useful for proving access to deleted directories.

```
USRCLASS.DAT\Local Settings\Software\Microsoft\Windows\Shell\Bags
USRCLASS.DAT\Local Settings\Software\Microsoft\Windows\Shell\BagMRU
NTUSER.DAT\Software\Microsoft\Windows\Shell\Bags
NTUSER.DAT\Software\Microsoft\Windows\Shell\BagMRU
```

> Use **ShellBagsExplorer** (Eric Zimmermann's tools) to parse shellbags into a readable format.

---

## Program Execution Artifacts

### UserAssist
Tracks GUI applications launched by the user (does **not** capture command-line executions). Values are ROT13-encoded:

```
NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist\{GUID}\Count
```

### AppCompatCache (ShimCache)
Tracks application execution for compatibility purposes. Records the file path and last modification time of executed binaries:

```
SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache
```

> Requires **AppCompatCacheParser** to parse.

### Amcache
Records metadata about recently executed applications, including SHA1 hash of the binary. Useful for identifying malware even after the file is deleted:

```
Amcache.hve\Root\File\{Volume GUID}\
```

> Use **AmcacheParser** to parse.

### BAM/DAM (Background/Desktop Activity Moderator)
Records the last execution time of processes per user SID:

```
SYSTEM\CurrentControlSet\Services\bam\UserSettings\{SID}
SYSTEM\CurrentControlSet\Services\dam\UserSettings\{SID}
```

---

## USB Device Artifacts

### Connected USB Storage Devices
```
SYSTEM\CurrentControlSet\Enum\USBSTOR
SYSTEM\CurrentControlSet\Enum\USB
```

Each entry includes vendor name, product name, and a unique serial number.

### Connection Timestamps
```
SYSTEM\CurrentControlSet\Enum\USBSTOR\Ven_Prod_Version\USBSerial#\Properties\{83da6326-97a6-4088-9453-a19231573b29}\
  0064 → First connection time
  0066 → Last connection time
  0067 → Last removal time
```

### Drive Letter / Volume Name
```
SOFTWARE\Microsoft\Windows Portable Devices\Devices
```

---

## Services
```
SYSTEM\CurrentControlSet\Services
```

Each subkey is a service. Look for:
- Services with `ImagePath` values pointing to unusual locations
- Services with recently modified timestamps
- Services with `Start` value `2` (automatic) that are not part of the known baseline

---

## User Accounts (SAM)
```
SAM\Domains\Account\Users
```

Contains local user accounts, last login time, login count, and password metadata. Requires SYSTEM privileges to access on a live system.

---

## Recommended Tooling

| Tool | Purpose |
|------|---------|
| `regedit.exe` | Built-in live registry viewer |
| RegRipper | Automated key extraction and reporting |
| Eric Zimmermann's tools (RECmd, ShellBagsExplorer, AppCompatCacheParser, AmcacheParser) | Best-in-class offline registry forensics |
| YARU | Open-source registry forensics utility |
