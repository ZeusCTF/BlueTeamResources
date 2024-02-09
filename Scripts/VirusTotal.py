import vt
#https://docs.virustotal.com/reference/scan-url
import requests
import json
import base64
import hashlib

key = ''

def url_scan(url):

    #prepares the request per the api requirements
    b64 = base64.b64encode(url.encode())
    scan = f"https://www.virustotal.com/api/v3/urls/{b64.decode()}"

    headers = {
        "accept": "application/json",
        "x-apikey": key
    }

    #loads the response data, and prints analysis information
    response = requests.get(scan, headers=headers)
    last_analysis_stats = json.loads(response.text)
    print(f"[*] Scanning URL {url}")
    print("[*] Results:")
    print(last_analysis_stats["data"]["attributes"]["last_analysis_stats"])

def file_report(file_hash):

    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"

    headers = {
        "accept": "application/json",
        "x-apikey": key
    }

    response = requests.get(url, headers=headers)

    print(response.text)

file_report('f5dc19126ac0a7bb1b998d0a6df319e2')

"""
#main decision tree
def main():

    print('What would you like to do:')
    print('Enter 1 to scan a URL')
    print('Enter 2 to lookup an IP address')
    print('Enter 3 to search a file hash.')
    print('Enter q to quit.')

    decision = input('')

    while decision != 'q':
        if decision == '1':
            view(path)
        elif decision == '2':
            edit(path)
        elif decision == '3':
            search(path)

        print('Enter 1 to view the entire plist file.')
        print('Enter 2 to add information or update the plist file.')
        print('Enter 3 to search for a specific key in the plist file.')
        print('Enter q to quit.')
        decision = input('What would you like to do next? (Enter q to quit) ')

main()
"""