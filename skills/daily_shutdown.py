import os
import time
import subprocess
import ctypes
import webbrowser
from datetime import datetime

# Configuration
WORKSPACE_DIR = r"C:\Users\mikas\OneDrive\antigravity-vison"
LOGS_DIR = os.path.join(WORKSPACE_DIR, "memories", "raw_logs")

def show_message_box(title, message):
    """
    Displays a modal message box (Windows Native).
    1 = OK/Cancel button
    48 = Exclamation Icon
    4096 = System Modal (On top)
    """
    return ctypes.windll.user32.MessageBoxW(0, message, title, 1 | 48 | 4096)

def run_git_backup():
    print("💾 Backing up Codebase (Git)...")
    try:
        os.chdir(WORKSPACE_DIR)
        # Check if git is initialized
        if not os.path.exists(os.path.join(WORKSPACE_DIR, ".git")):
            print("⚠️ Git not initialized. Skipping code backup.")
            return
        
        # Add all
        subprocess.run(["git", "add", "."], check=False)
        
        # Commit with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto-Backup: Goodnight Protocol {timestamp}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=False)
        
        print(f"✅ Code committed: {commit_msg}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

def open_log_folder():
    print(f"📂 Opening Log Directory: {LOGS_DIR}")
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    os.startfile(LOGS_DIR)

def main():
    print("🌙 ANTIGRAVITY SHUTDOWN PROTOCOL INITIATED 🌙")
    print("---------------------------------------------")
    
    # 1. Backup Code
    run_git_backup()
    
    # 2. Open Folder
    open_log_folder()
    
    # 3. Nag User (The Memory Reminder)
    print("\n🛑 WAITING FOR USER ACTION: EXPORT CHAT")
    
    msg = (
        "Project Antigravity Requesting Backup:\n\n"
        "1. Please use the VS Code 'Export Chat' button.\n"
        "2. Save the file into the folder that just opened.\n"
        "3. Suggested Name: safechat_" + datetime.now().strftime("%Y%m%d") + ".md\n\n"
        "Have you secured the memory?"
    )
    
    result = show_message_box("Don't Forget Me! 🐘", msg)
    
    if result == 1: # OK Pressed
        print("✅ Memory Secured. Sleep well, Master.")
        time.sleep(2)
    else: # Cancel Pressed
        print("⚠️ Warning: Memory Risk Accepted.")
        time.sleep(1)

if __name__ == "__main__":
    main()
