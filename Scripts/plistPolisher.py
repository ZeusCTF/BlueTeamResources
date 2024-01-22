"""
Three plist file types exist; binary, xml, and json (though the first two seem to be the most common):

file org.virtualbox.app.VirtualBox.plist
org.virtualbox.app.VirtualBox.plist: Apple binary property list

file org.virtualbox.app.VirtualBox.plist1
org.virtualbox.app.VirtualBox.plist1: XML 1.0 document text, ASCII text

You can convert the plist files to xml with something like the below(which is what I did in the above example):
plutil -convert xml1 <file>
With both of the forms above being vaild, binary is just more efficient on disk.
"""
import argparse
import plistlib

xml_plist_path = '/Users/barryallen/Test/org.virtualbox.app.VirtualBox.plist1'

def view(path):
    # Open the plist file
    with open(path, 'rb') as fp:
        # Load the plist data, and print it in a more readable format
        data = plistlib.load(fp)
        for k,v in data.items():
            print(k,v)
        fp.close()

def edit(path):
    # Open the plist file
    with open(path, 'rb') as fp:
        data = plistlib.load(fp)
        key = input('Enter the new key, or a key to be updated: ')
        value = input('Enter the associated value: ')
        # Make changes to the plist data
        data[key] = value
        with open(xml_plist_path, 'wb') as fp:
            plistlib.dump(data, fp)
            fp.close()

def search(path):
    with open(path, 'rb') as fp:
        data = plistlib.load(fp)
        key = input('Enter the key name you are looking for: ')
        print()
        print('Below is the associated value:')
        print(data[key])


def main():
    # Grab file path
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='Please provide the full path to the plist file')
    args = parser.parse_args()
    path = args.file

    print('What would you like to do:')
    print('Enter 1 to view the entire plist file.')
    print('Enter 2 to add information or update the plist file.')
    print('Enter 3 to search for a specific key in the plist file.')
    print('Enter q to quit.')
    while True:
        decision = input('')
        if decision == 1:
            view(path)
main()