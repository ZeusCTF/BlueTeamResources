#!/bin/bash

#Just a quick script written to check a few methods of persistence that are used on Macs.
#Note that this script does not show all of the various methods, and should mainly be used as a tool to determine where further investigative efforts should be spent.


#Checking Launch Agents
echo "Checking the contents of /Library/LaunchAgents and /Library/LaunchDaemons."
ls -la /Library/Launch*

echo "Also checking the home directory of the current user:"
ls -la ~/Library/LaunchAgents

echo "Do any crontabs exist for the current user?"
crontab -l
#/private/var/at/tabs should contain ALL crontabs on the system, but requires root access to view (similar to at jobs)

echo "Checking for periodic scripts"
ls ls /etc/periodic/*
#Note: this is not commonly used for malware

echo "Collection of .plist files"
ls -la /Library/Preferences

echo "Any dangerous strings/settings detected?"
echo "Searching for the RunAtLoad key"
grep -R RunAtLoad /Library/Preferences

echo "Dynamic libraries:"
la -la ~/lib
ls -la /usr/local/lib
ls -la /usr/lib

echo ""
echo "Does a custom library path exist?"
echo ""

if env | grep -q "LD_LIBRARY_PATH"; then
  echo "LD_LIBRARY_PATH variable is present"
else
  echo "LD_LIBRARY_PATH variable is not present"
fi

echo "Checking for the existance of shell startup scripts"
directory_path="/Users"
# Check if the path exists
if [ -d "$directory_path" ]; then
    for folder in "$directory_path"/*; do
            echo "Folder: $folder"
            ls $folder/.zshrc
            ls $folder/.bashrc
    done
fi

echo "Checking for the existance of custom preference panes"
if [ -d "$directory_path" ]; then
    for folder in "$directory_path"/*; do
            echo "Folder: $folder/Library/PreferencePanes"
            ls -la $folder/Library/PreferencePanes
    done
    echo "Are there any preference panes installed for all users?"
    ls -la /Library/PreferencePanes
fi

echo "Has a malicious startup command been added to the terminal?"
  if [ -d "$directory_path" ]; then
    echo "Checking $folder/Library/Preferences/com.apple.Terminal.plist"
    for folder in "$directory_path"/*; do
            plutil -p $folder/Library/Preferences/com.apple.Terminal.plist | grep "CommandString"
    done
fi

uuid=$(ioreg -rd1 -c IOPlatformExpertDevice | awk -F'"' '/IOPlatformUUID/{print $4}')
echo "Device UUID: $uuid"
echo "Checking for startup apps:"
plutil -p ~/Library/Preferences/ByHost/com.apple.loginwindow.$uuid.plist

echo "Checking for the existence of emond rules"
ls -la /etc/emond.d/rules/

echo "Do any folder action scripts exist?"
ls -a /Library/Scripts/Folder\ Action\ Scripts/

