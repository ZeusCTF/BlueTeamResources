#!/bin/bash

#Checking Launch Agents
echo "Checking the contents of /Library/LaunchAgents and /Library/LaunchDaemons."
ls -la /Library/Launch*

echo "Also checking the home directory of the current user:"
ls -la ~/Library/LaunchAgents