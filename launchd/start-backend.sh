#!/bin/zsh
# Startup wrapper for launchd — activates the venv before running the backend

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"

BACKEND="/Users/jackyli/Library/CloudStorage/OneDrive-Personal/Documents/Githubs/Regnology-Vizor-PS-Chatbot/backend"

cd "$BACKEND"
source .venv/bin/activate
exec python main.py
