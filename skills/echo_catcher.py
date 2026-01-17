import time
import os
import datetime
import tkinter as tk

def get_clipboard_text():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    try:
        content = root.clipboard_get()
        root.destroy()
        return content
    except tk.TclError:
        root.destroy()
        return ""

def save_to_log(content):
    # Ensure directory exists
    log_dir = os.path.join(os.path.dirname(__file__), "..", "memories", "raw_logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # File name: echo_log_YYYY_MM_DD.md
    today = datetime.datetime.now().strftime("%Y_%m_%d")
    file_path = os.path.join(log_dir, f"echo_log_{today}.md")

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    
    separator = f"\n\n--- [Captured at {timestamp}] ---\n\n"
    
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(separator)
            f.write(content)
        print(f"[{timestamp}] ✅ Saved {len(content)} chars to {os.path.basename(file_path)}")
    except Exception as e:
        print(f"❌ Error saving: {e}")

def main():
    print("🎧 Antigravity Echo Catcher is Listening...")
    print("👉 Usage: Just press Ctrl+A -> Ctrl+C in the chat window.")
    print("💾 Logs will be saved to: /memories/raw_logs/")
    
    last_content = ""
    
    while True:
        current_content = get_clipboard_text()
        
        if current_content and current_content != last_content:
            # Simple heuristic: If it's chat-like (long text), save it.
            # Actually, save everything. The user decides what to copy.
            save_to_log(current_content)
            last_content = current_content
            
        time.sleep(1.0) # Check every second

if __name__ == "__main__":
    main()
