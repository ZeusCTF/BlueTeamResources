#!/usr/bin/env python3
"""
virustotal_lookup.py — VirusTotal API CLI Tool

Performs URL, IP address, and file hash lookups against the VirusTotal API (v3).
If a file hash is not found in the VT database, optionally uploads the file for analysis.

Usage:
    python virustotal_lookup.py --url https://example.com/
    python virustotal_lookup.py --ip 8.8.8.8
    python virustotal_lookup.py --hash <md5_hash>
    python virustotal_lookup.py --interactive

Requirements:
    pip install requests

API Key:
    Set the VT_API_KEY environment variable, or pass it via --key.
    A free API key can be obtained at https://www.virustotal.com/gui/join-us
"""

import argparse
import base64
import json
import os
import sys
import requests


BASE_URL = "https://www.virustotal.com/api/v3"


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _headers(api_key: str) -> dict:
    return {
        "accept": "application/json",
        "x-apikey": api_key,
    }


def _print_analysis_stats(stats: dict) -> None:
    """Pretty-print last_analysis_stats from a VT response."""
    width = max(len(k) for k in stats) + 2
    for label, count in sorted(stats.items(), key=lambda x: -x[1]):
        bar = "█" * min(count, 40)
        print(f"  {label:<{width}} {count:>4}  {bar}")


# ---------------------------------------------------------------------------
# Lookup functions
# ---------------------------------------------------------------------------

def lookup_url(url: str, api_key: str) -> None:
    """
    Look up a URL in the VirusTotal database.

    VirusTotal requires URLs to be base64-encoded (without padding) for the v3 API.
    """
    encoded = base64.urlsafe_b64encode(url.encode()).rstrip(b"=").decode()
    endpoint = f"{BASE_URL}/urls/{encoded}"

    print(f"\n[*] Looking up URL: {url}")

    try:
        response = requests.get(endpoint, headers=_headers(api_key), timeout=15)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"[!] HTTP error: {e}")
        print("    Ensure the URL includes the scheme (https://) and a trailing slash.")
        return
    except requests.exceptions.RequestException as e:
        print(f"[!] Request failed: {e}")
        return

    data = response.json()
    stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})

    if not stats:
        print("[!] No analysis data returned. The URL may not have been scanned yet.")
        return

    print("[*] Analysis results:")
    _print_analysis_stats(stats)


def lookup_ip(ip: str, api_key: str) -> None:
    """Look up an IP address in the VirusTotal database, including WHOIS data."""
    endpoint = f"{BASE_URL}/ip_addresses/{ip}"

    print(f"\n[*] Looking up IP: {ip}")

    try:
        response = requests.get(endpoint, headers=_headers(api_key), timeout=15)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"[!] HTTP error: {e}")
        return
    except requests.exceptions.RequestException as e:
        print(f"[!] Request failed: {e}")
        return

    data = response.json().get("data", {}).get("attributes", {})
    stats = data.get("last_analysis_stats", {})

    if stats:
        print("[*] Analysis results:")
        _print_analysis_stats(stats)
    else:
        print("[!] No analysis stats returned.")

    whois = data.get("whois")
    if whois:
        print("\n[*] WHOIS information:")
        # Print only the first 20 lines to avoid overwhelming output
        lines = whois.strip().splitlines()
        for line in lines[:20]:
            print(f"  {line}")
        if len(lines) > 20:
            print(f"  ... ({len(lines) - 20} more lines — run with --full-whois to see all)")
    else:
        print("[!] No WHOIS data available for this IP.")


def _upload_file(file_hash: str, api_key: str) -> dict | None:
    """
    Prompt the user to upload a file not found in the VT database.

    Returns the analysis stats dict if successful, or None on failure.
    """
    print("[*] This file hash was not found in the VirusTotal database.")
    file_path = input("    Enter the full path to the file to upload (or press Enter to skip): ").strip()

    if not file_path:
        print("[*] Upload skipped.")
        return None

    if not os.path.isfile(file_path):
        print(f"[!] File not found: {file_path}")
        return None

    file_name = os.path.basename(file_path)
    print(f"[*] Uploading: {file_name}")

    try:
        with open(file_path, "rb") as f:
            upload_response = requests.post(
                f"{BASE_URL}/files",
                files={"file": (file_name, f)},
                headers=_headers(api_key),
                timeout=60,
            )
        upload_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[!] Upload failed: {e}")
        print("    You can upload the file manually at https://www.virustotal.com")
        return None

    if "analysis" not in upload_response.text:
        print("[!] Upload response did not confirm analysis. Check the VT site manually.")
        return None

    print("[*] Upload complete. Fetching results...")

    try:
        result_response = requests.get(
            f"{BASE_URL}/files/{file_hash}",
            headers=_headers(api_key),
            timeout=15,
        )
        result_response.raise_for_status()
        return result_response.json().get("data", {}).get("attributes", {}).get("last_analysis_stats")
    except requests.exceptions.RequestException as e:
        print(f"[!] Failed to fetch results after upload: {e}")
        return None


def lookup_hash(file_hash: str, api_key: str) -> None:
    """
    Look up a file hash (MD5, SHA1, or SHA256) in the VirusTotal database.

    If the hash is not found, offers to upload the file for analysis.
    """
    endpoint = f"{BASE_URL}/files/{file_hash}"

    print(f"\n[*] Looking up file hash: {file_hash}")

    try:
        response = requests.get(endpoint, headers=_headers(api_key), timeout=15)
    except requests.exceptions.RequestException as e:
        print(f"[!] Request failed: {e}")
        return

    if response.status_code == 404 or "NotFoundError" in response.text:
        stats = _upload_file(file_hash, api_key)
    else:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"[!] HTTP error: {e}")
            return
        stats = response.json().get("data", {}).get("attributes", {}).get("last_analysis_stats")

    if stats:
        print("[*] Analysis results:")
        _print_analysis_stats(stats)
    else:
        print("[!] No analysis data available.")


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------

def interactive_mode(api_key: str) -> None:
    """Run a simple interactive REPL for repeated lookups."""
    print("\nVirusTotal Lookup Tool — Interactive Mode")
    print("  1) Look up a URL")
    print("  2) Look up an IP address")
    print("  3) Look up a file hash (MD5/SHA1/SHA256)")
    print("  q) Quit\n")

    while True:
        choice = input("Choice: ").strip().lower()

        if choice == "q":
            break
        elif choice == "1":
            url = input("URL: ").strip()
            if url:
                lookup_url(url, api_key)
        elif choice == "2":
            ip = input("IP address: ").strip()
            if ip:
                lookup_ip(ip, api_key)
        elif choice == "3":
            file_hash = input("File hash: ").strip()
            if file_hash:
                lookup_hash(file_hash, api_key)
        else:
            print("[!] Invalid choice. Enter 1, 2, 3, or q.")

        print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="VirusTotal API lookup tool for URLs, IPs, and file hashes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--key", metavar="API_KEY",
                        help="VirusTotal API key (overrides VT_API_KEY env variable)")
    parser.add_argument("--url", metavar="URL",
                        help="URL to look up")
    parser.add_argument("--ip", metavar="IP",
                        help="IP address to look up")
    parser.add_argument("--hash", metavar="HASH",
                        help="File hash to look up (MD5, SHA1, or SHA256)")
    parser.add_argument("--interactive", action="store_true",
                        help="Launch interactive mode for multiple lookups")

    args = parser.parse_args()

    # Resolve API key: CLI flag > environment variable > prompt
    api_key = args.key or os.environ.get("VT_API_KEY")
    if not api_key:
        api_key = input("Enter your VirusTotal API key: ").strip()
    if not api_key:
        print("[!] No API key provided. Exiting.")
        sys.exit(1)

    # Dispatch
    if args.interactive:
        interactive_mode(api_key)
    elif args.url:
        lookup_url(args.url, api_key)
    elif args.ip:
        lookup_ip(args.ip, api_key)
    elif args.hash:
        lookup_hash(args.hash, api_key)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
