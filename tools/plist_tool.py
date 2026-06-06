#!/usr/bin/env python3
"""
plist_tool.py — macOS Plist File Utility

View, search, edit, and convert macOS property list (.plist) files.
Supports binary, XML, and JSON plist formats.

Usage:
    python plist_tool.py <file.plist>                  # Interactive mode
    python plist_tool.py <file.plist> --view           # Print all keys and values
    python plist_tool.py <file.plist> --search KEY     # Look up a specific key
    python plist_tool.py <file.plist> --set KEY VALUE  # Add or update a key
    python plist_tool.py <file.plist> --convert xml    # Convert to xml/binary/json
    python plist_tool.py <file.plist> --keys           # List all top-level keys

Notes:
    - Binary plists are read transparently; no manual conversion required before use.
    - To convert between formats, plutil must be available on the system (macOS only).
    - Editing writes directly to the source file. Keep a backup before modifying.

Plist Format Reference:
    Binary:  file.plist: Apple binary property list
    XML:     file.plist: XML 1.0 document text
    Convert: plutil -convert xml1 <file>   # Manual CLI conversion if needed
"""

import argparse
import plistlib
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Core plist operations
# ---------------------------------------------------------------------------

def load_plist(path: Path) -> dict:
    """Load a plist file (binary or XML) and return its contents as a dict."""
    with open(path, "rb") as f:
        return plistlib.load(f)


def save_plist(path: Path, data: dict) -> None:
    """Write a dict back to a plist file in binary format."""
    with open(path, "wb") as f:
        plistlib.dump(data, f)


def view(path: Path) -> None:
    """Print all key-value pairs in the plist, one per line."""
    data = load_plist(path)
    if not data:
        print("(empty plist)")
        return

    max_key_len = max(len(str(k)) for k in data) if data else 0
    for key, value in sorted(data.items(), key=lambda x: str(x[0])):
        print(f"  {str(key):<{max_key_len + 2}}  {value!r}")


def list_keys(path: Path) -> None:
    """Print all top-level keys in the plist."""
    data = load_plist(path)
    keys = sorted(str(k) for k in data.keys())
    print(f"  {len(keys)} top-level key(s):\n")
    for key in keys:
        value_type = type(data[key]).__name__
        print(f"  {key}  ({value_type})")


def search(path: Path, key: str) -> None:
    """Look up a specific key and print its value."""
    data = load_plist(path)
    if key in data:
        print(f"  {key}: {data[key]!r}")
    else:
        # Case-insensitive fallback
        matches = [k for k in data if str(k).lower() == key.lower()]
        if matches:
            print(f"  Key '{key}' not found exactly. Did you mean one of these?")
            for match in matches:
                print(f"    {match}: {data[match]!r}")
        else:
            print(f"  [!] Key '{key}' not found in plist.")
            print(f"      Use --keys to see all available keys.")


def set_value(path: Path, key: str, value: str) -> None:
    """
    Add or update a key in the plist.

    Values are stored as strings. For other types, modify the source directly
    or use plutil on the command line.
    """
    data = load_plist(path)
    existed = key in data
    data[key] = value
    save_plist(path, data)

    action = "Updated" if existed else "Added"
    print(f"  [{action}] {key} = {value!r}")


def convert(path: Path, fmt: str) -> None:
    """
    Convert a plist to xml, binary, or json format using plutil.

    Requires macOS with plutil available (standard on all macOS systems).
    """
    fmt_map = {
        "xml": "xml1",
        "binary": "binary1",
        "json": "json",
    }

    if fmt not in fmt_map:
        print(f"  [!] Unknown format '{fmt}'. Choose from: xml, binary, json")
        return

    plutil_fmt = fmt_map[fmt]
    result = subprocess.run(
        ["plutil", "-convert", plutil_fmt, str(path)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"  Converted to {fmt} format: {path}")
    else:
        print(f"  [!] Conversion failed: {result.stderr.strip()}")


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------

MENU = """
  Operations:
    1) View all key-value pairs
    2) List top-level keys
    3) Search for a specific key
    4) Add or update a key
    5) Convert to a different format
    6) Switch to a different file
    q) Quit
"""


def interactive(path: Path) -> None:
    """Run an interactive REPL for plist inspection and editing."""
    print(f"\n  Loaded: {path}")

    while True:
        print(MENU)
        choice = input("  Choice: ").strip().lower()

        if choice == "q":
            break
        elif choice == "1":
            print()
            view(path)
        elif choice == "2":
            print()
            list_keys(path)
        elif choice == "3":
            key = input("  Key name: ").strip()
            print()
            search(path, key)
        elif choice == "4":
            key = input("  Key name: ").strip()
            value = input("  Value (stored as string): ").strip()
            set_value(path, key, value)
        elif choice == "5":
            fmt = input("  Format (xml / binary / json): ").strip().lower()
            convert(path, fmt)
        elif choice == "6":
            new_path_str = input("  New file path: ").strip()
            new_path = Path(new_path_str)
            if validate_plist(new_path):
                path = new_path
                print(f"  Switched to: {path}")
        else:
            print("  [!] Invalid choice.")

        print()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_plist(path: Path) -> bool:
    """
    Return True if the file exists and is a valid plist.
    Prints a descriptive error and returns False otherwise.
    """
    if not path.exists():
        print(f"[!] File not found: {path}")
        return False

    try:
        load_plist(path)
        return True
    except plistlib.InvalidFileException:
        print(f"[!] '{path}' is not a valid plist file.")
        return False
    except Exception as e:
        print(f"[!] Failed to read '{path}': {e}")
        return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="View, search, edit, and convert macOS plist files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("file", help="Path to the .plist file")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--view", action="store_true",
                      help="Print all key-value pairs")
    mode.add_argument("--keys", action="store_true",
                      help="List all top-level keys with their types")
    mode.add_argument("--search", metavar="KEY",
                      help="Look up the value of a specific key")
    mode.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"),
                      help="Add or update a key with a string value")
    mode.add_argument("--convert", metavar="FORMAT", choices=["xml", "binary", "json"],
                      help="Convert the plist to xml, binary, or json format")

    args = parser.parse_args()
    path = Path(args.file)

    if not validate_plist(path):
        sys.exit(1)

    if args.view:
        view(path)
    elif args.keys:
        list_keys(path)
    elif args.search:
        search(path, args.search)
    elif args.set:
        set_value(path, args.set[0], args.set[1])
    elif args.convert:
        convert(path, args.convert)
    else:
        interactive(path)


if __name__ == "__main__":
    main()
