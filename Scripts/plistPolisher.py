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

def view(path):
    # Open the plist file
    with open(path, 'rb') as fp:
        # Load the plist data, and print it in a more readable format
        data = plistlib.load(fp)
        for k, v in data.items():
            print(k, v)

def edit(path):
    # Open the plist file
    with open(path, 'rb') as fp:
        data = plistlib.load(fp)
        key = input('Enter the new key, or a key to be updated: ')
        value = input('Enter the associated value: ')
        # Make changes to the plist data
        data[key] = value
        with open(path, 'wb') as fp:
            plistlib.dump(data, fp)

#searches for a specific key's value
def search(path):
    with open(path, 'rb') as fp:
        data = plistlib.load(fp)
        key = input('Enter the key name you are looking for: ')
        print()
        print('Below is the associated value:')
        print(data[key])

#function for converting a plist file into a specified format
def convert(path):
    import subprocess
    print('Which format do you wish to convert the file to?: ')
    print('[1] for xml')
    print('[2] for binary')
    print('[3] for json')
    format = input()
    while format:
        if format == '1':
            subprocess.run(["plutil", "-convert", "xml1", path])
            break
        elif format == '2':
            subprocess.run(["plutil", "-convert", "binary1", path])
            break
        elif format == '3': 
            subprocess.run(["plutil", "-convert", "json", path])
            break
        else:
            print('Invalid option, please re-enter a valid operation.')
            format = input()

def main():
    # Grab file path
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='Please provide the full path to the plist file')
    args = parser.parse_args()
    path = args.file
    correct = 0

    while correct == 0:
        try:
            with open(path, 'rb') as fp:
                plist_data = plistlib.load(fp)
            print(f'{path} is a valid plist file.')
            correct = 1
        except plistlib.InvalidFileException:
            print(f'{path} is not a valid plist file.')
            path = input('Please enter the full correct path to a .plist file: ')


    print('What would you like to do:')
    print('Enter 1 to view the entire plist file.')
    print('Enter 2 to add information or update the plist file.')
    print('Enter 3 to search for a specific key in the plist file.')
    print('Enter 4 to convert the plist file into a different format.')
    print('Enter 5 to provide a new file to modify.')
    print('Enter q to quit.')

    decision = input('')

    while decision != 'q':
        if decision == '1':
            view(path)
        elif decision == '2':
            edit(path)
        elif decision == '3':
            search(path)
        elif decision == '4':
            convert(path)
        elif decision == '5':
            print('Please enter the new path:')
            path = input()
        print('Enter 1 to view the entire plist file.')
        print('Enter 2 to add information or update the plist file.')
        print('Enter 3 to search for a specific key in the plist file.')
        print('Enter 4 to convert the plist file into a different format.')
        print('Enter 5 to provide a new file to modify.')
        print('Enter q to quit.')
        decision = input('What would you like to do next? (Enter q to quit) ')

main()
