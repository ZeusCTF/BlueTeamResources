import vt
#https://docs.virustotal.com/reference/scan-url
import requests
import json
import base64

key = '5a67195f10bcf4e90670fe7dab139ae2d0c358b57d8b92f32a9a42206f71a212'

def url_scan(url):

    #Prepares the request per the api requirements
    b64 = base64.b64encode(url.encode())
    scan = f"https://www.virustotal.com/api/v3/urls/{b64.decode()}"

    headers = {
        "accept": "application/json",
        "x-apikey": key
    }

    #Loads the response data, and prints analysis information
    response = requests.get(scan, headers=headers)
    last_analysis_stats = json.loads(response.text)
    print(f"[*] Scanning URL {url}")
    print("[*] Results:")
    print(last_analysis_stats["data"]["attributes"]["last_analysis_stats"])

def file_report(file_hash):

    #This section takes a file hash and checks it against the already existing VT database
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"

    headers = {
        "accept": "application/json",
        "x-apikey": key
    }

    response = requests.get(url, headers=headers)

    #If the prior checks indicate the file wasn't already apart of the VT database, we can upload it with the below 
    if "NotFound" in response.text:
        print("Unique file detected!")
        print('Please provide the full path to the designated file, an upload to the VirusTotal API will be attempted')
        path = input("")

        #build the file name to pass into the request per VT docs
        file_name = ""
        for char in path[::-1]:
            if char != "/":
                file_name += char
            else:
                print(f"Attempting to upload: {file_name}")
                break
            
        url = "https://www.virustotal.com/api/v3/files"
        files = { "file": (file_name, open(path, "rb")) }
        headers = {"accept": "application/json"}

        
        response = requests.post(url, files=files, headers=headers)

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