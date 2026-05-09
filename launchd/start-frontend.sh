#!/bin/zsh
# Wrapper script for launchd — sets up nvm environment before starting the frontend

export NVM_DIR="$HOME/.nvm"
# Load nvm
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"

cd /Users/jackyli/Library/CloudStorage/OneDrive-Personal/Documents/Githubs/Regnology-Vizor-PS-Chatbot/frontend

exec npm run preview
