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
