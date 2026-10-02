import subprocess
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class GitAutoPusher(FileSystemEventHandler):
    def __init__(self):
        self.last_sync = 0
        self.cooldown = 4  # Wait 4 seconds between pushes

    def run_cmd(self, command):
        return subprocess.run(command, shell=True, text=True, capture_output=True).stdout.strip()

    def sync(self):
        if time.time() - self.last_sync < self.cooldown:
            return

        # Check for uncommitted changes
        changes = self.run_cmd("git status --porcelain")
        if not changes:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[!] Changes detected at {timestamp}. Syncing...")

        self.run_cmd("git add .")
        self.run_cmd(f'git commit -m "Auto-update: {timestamp}"')
        self.run_cmd("git push origin main")
        
        print("[✓] Pushed to github.com/Simone2048/Resonix")
        self.last_sync = time.time()

    def on_modified(self, event):
        if ".git" not in event.src_path:
            self.sync()

    def on_created(self, event):
        if ".git" not in event.src_path:
            self.sync()

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(GitAutoPusher(), path=".", recursive=True)
    
    print("[*] Monitoring Desktop/Resonix... (Press Ctrl+C to stop)")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] Stopped.")
    observer.join()