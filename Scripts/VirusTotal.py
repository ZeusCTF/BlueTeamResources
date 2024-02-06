import vt
#https://docs.virustotal.com/reference/scan-url
import requests

url = "https://www.virustotal.com/api/v3/urls"

payload = { "url": "string" }
headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
    "x-apikey": "API KEY"
}

response = requests.post(url, data=payload, headers=headers)

print(response.text)


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