---
title: Obsidian Vault Sync with Git/GitHub
date: 2026-03-27
log: 001
kind: Guide
subtitle: A comprehensive guide to syncing your knowledge vault across devices — manually and with automation.
summary: A comprehensive guide to syncing your Obsidian vault across devices using Git and GitHub — covering initial setup, SSH keys, daily workflow, and automation scripts for both Ubuntu and Android (Termux).
description: A comprehensive guide to syncing your Obsidian vault across devices using Git and GitHub, including automation scripts for Ubuntu and Android.
page_title: Obsidian Git Sync Guide
---

If you use [Obsidian](https://obsidian.md/) for note-taking, you've probably hit the sync problem: how do you keep your vault consistent across your laptop, desktop, and phone — without paying for Obsidian Sync?

The answer? **Git and GitHub.** It's free, reliable, version-controlled, and once set up, can be fully automated with a simple script. This guide walks you through the entire process.

## // 01. Setting Up Git for Your Vault {#setup}

### Install Git

If you haven't already, install Git on your system:

```bash title="Terminal"
# Ubuntu / Debian
sudo apt update && sudo apt install git

# macOS (via Homebrew)
brew install git

# Verify installation
git --version
```

### Initialize a Repository in Your Vault

Navigate to your Obsidian vault folder and initialize Git:

```bash title="Terminal"
cd ~/your-obsidian-vault
git init
git branch -M main
```

### Create a GitHub Repository

- Go to [github.com/new](https://github.com/new)
- Name it something like `obsidian-vault`
- Set it to **Private** — your notes are personal
- Do **not** initialize with a README (you already have local files)

### Link Local to Remote

```bash title="Terminal"
git remote add origin git@github.com:YourUsername/your-vault.git
git add .
git commit -m "Initial commit: vault setup"
git push -u origin main
```

### Set Up SSH Keys

SSH keys let you push and pull without typing your password every time.

```bash title="Terminal"
# Generate a new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Start the SSH agent
eval "$(ssh-agent -s)"

# Add your key
ssh-add ~/.ssh/id_ed25519

# Copy the public key to clipboard
cat ~/.ssh/id_ed25519.pub
```

Then go to [GitHub → Settings → SSH Keys](https://github.com/settings/keys), click **"New SSH Key"**, paste your key, and save.

## // 02. The Basic Git Workflow {#workflow}

Once everything is linked, here's the daily workflow:

```bash title="Daily Sync Workflow"
# Pull the latest changes (always do this first)
git pull origin main

# Stage all changes
git add .

# Commit with a message
git commit -m "sync: updated notes"

# Push to GitHub
git push origin main
```

> **Handling Merge Conflicts:** If you edited the same note on two devices without syncing, Git will flag a conflict. Open the file, look for the `<<<<<<<` markers, choose which version to keep, then commit and push again.

## // 03. Best Practices {#best-practices}

### Set Up .gitignore

Create a `.gitignore` file in your vault root to exclude Obsidian workspace clutter:

```text title=".gitignore"
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache
.trash/
.DS_Store
```

- Commit frequently — at the end of every session is a good rule
- Always pull before you start editing on a new device
- Keep your repo private if your notes contain anything sensitive

---

## // 04. Automating the Sync with Scripts {#automation}

Typing `git add`, `git commit`, `git push` every time gets old fast. Let's automate it with a single command: `vaultsync`.

### The Desktop Sync Script (Linux, macOS, Windows)

Open your terminal and create the file:

```bash title="Terminal"
nano ~/vaultsync.sh
```

Paste the following code:

```bash title="vaultsync.sh // Bash"
#!/bin/bash

# Configuration
VAULT_PATH="$HOME/obsidian-vault" # Update this if your path is different

# 1. Navigate to Vault
cd "$VAULT_PATH" || { echo "❌ Vault directory not found!"; exit 1; }

echo "---------------------------------------"
echo "🚀 Starting Obsidian-Vault Sync..."
echo "---------------------------------------"

# 2. Check for Git Lock files (prevents errors if a previous sync crashed)
if [ -f .git/index.lock ]; then
    rm .git/index.lock
    echo "⚠️  Removed existing git lock file."
fi

# 3. Pull latest changes
echo "📥 Pulling from Remote..."
git pull origin main

# 4. Add and Commit
# This adds all changes and uses a timestamped message
echo "📤 Committing changes..."
git add .
git commit -m "desktop sync: $(date +'%Y-%m-%d %H:%M:%S')"

# 5. Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo "---------------------------------------"
echo "✅ Sync Complete! Your vault is updated."
echo "---------------------------------------"
```

### Make it Executable and Global

To run this by simply typing `vaultsync`, follow the steps for your operating system:

#### Linux / macOS

```bash title="Terminal"
# 1. Make the script executable
chmod +x ~/vaultsync.sh

# 2. Move it to your local bin (so it's in your PATH)
sudo mv ~/vaultsync.sh /usr/local/bin/vaultsync

# 3. Test it — just type from any directory
vaultsync
```

#### Windows (Git Bash)

If you're on Windows, you can run this bash script using the Git Bash terminal.

```bash title="Git Bash"
# 1. Make sure it's saved in your home directory
mv vaultsync.sh ~/vaultsync.sh

# 2. Add an alias to your .bashrc file
echo "alias vaultsync='~/vaultsync.sh'" >> ~/.bashrc
source ~/.bashrc

# 3. Test it — just type
vaultsync
```

---

### The Android Sync Script (Termux)

Open **Termux** and follow these steps to create the shortcut:

(1) Open your bash configuration:

```bash title="Termux"
nano ~/.bashrc
```

(2) Scroll to the bottom and paste this code:

```bash title=".bashrc // Bash Function"
# Obsidian-Vault Sync Shortcut

vaultsync() {
    echo "Starting Sync for obsidian-vault..."
    cd /storage/emulated/0/obsidian-vault
    echo "📥 Pulling changes from GitHub..."
    git pull
    echo "📤 Pushing changes to GitHub..."
    git add .
    # This automatically adds the date and time to your commit message
    git commit -m "mobile sync: $(date +'%Y-%m-%d %H:%M:%S')"
    git push
    echo "✅ Sync Complete!"
}
```

(3) Save and Exit: Press `Ctrl + O`, then `Enter`, then `Ctrl + X`.

(4) Reload the config:

```bash title="Termux"
source ~/.bashrc
```

Now just type `vaultsync` in Termux and your vault syncs instantly.

---

## // 05. Error Handling & Tips {#error-handling}

- The Ubuntu script already handles stale `.git/index.lock` files — a common issue after interrupted syncs
- Add `set -e` at the top of your script to stop execution on any error
- You can add logging with: `echo "$(date) - Sync successful" >> ~/vaultsync.log`
- Use `git stash` before pulling if you want to test changes without risking conflicts

> **End goal:** One command — `vaultsync` — on any device, and your entire knowledge vault is backed up, version-controlled, and in sync. No subscriptions, no third-party apps. Just Git.

---

*— El Mehdi // sudoself.dev*
