import plistlib
from biplist import *
try:
    plist = readPlist('/Users/barryallen/Library/Preferences/com.apple.PhotoBooth.plist')
    print(plist)
except(InvalidPlistException, NotBinaryPlistException) as e:
    print("Not a plist:", e)



# Specify the path to your plist file
plist_path = '/Users/barryallen/Library/Preferences/com.apple.PhotoBooth.plist'

