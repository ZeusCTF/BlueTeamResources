#!/bin/bash

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