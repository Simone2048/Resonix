import os
import random
import subprocess
import time
from datetime import datetime

# Automatically sets the repository path to the folder where this script lives
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(REPO_PATH, "uploader.log")

# Check intervals in seconds (e.g., 300 to 600s = 5 to 10 minutes)
MIN_INTERVAL = 300
MAX_INTERVAL = 600

COMMIT_MESSAGES = [
    "Update project files",
    "Minor fixes and code improvements",
    "Refactor module implementation",
    "Progress update on Resonix",
    "Update assets and core functions",
    "WIP: updating implementation details",
    "Code adjustments and cleanups"
]

def log(message):
    """Prints to console and appends to uploader.log."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    entry = f"{timestamp} {message}"
    print(entry)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass

def run_git_command(args, cwd):
    """Executes a Git command and returns (success: bool, output: str)."""
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def get_current_branch(repo_path):
    """Automatically detects the current active branch (main, master, etc.)."""
    success, branch = run_git_command(["git", "branch", "--show-current"], repo_path)
    return branch if success and branch else "main"

def has_changes(repo_path):
    """Checks for modified, new, or deleted files."""
    success, output = run_git_command(["git", "status", "--porcelain"], repo_path)
    return success and len(output) > 0

def auto_push_loop():
    branch = get_current_branch(REPO_PATH)
    log(f"Started background uploader.")
    log(f"Active Directory: {REPO_PATH}")
    log(f"Active Branch: {branch}")

    while True:
        try:
            if has_changes(REPO_PATH):
                log("Local modifications detected!")

                # Stage all changes
                run_git_command(["git", "add", "."], REPO_PATH)

                # Commit changes with a humanized message
                msg = f"{random.choice(COMMIT_MESSAGES)} ({datetime.now().strftime('%b %d, %H:%M')})"
                success, out = run_git_command(["git", "commit", "-m", msg], REPO_PATH)

                if success:
                    log(f"Committed: '{msg}'")

                    # Push to the detected branch
                    push_success, push_out = run_git_command(["git", "push", "origin", branch], REPO_PATH)
                    if push_success:
                        log("Successfully pushed to GitHub!")
                    else:
                        log(f"Push failed: {push_out}")
                else:
                    log(f"Commit failed or clean: {out}")
            else:
                log("No changes detected. Working tree clean.")

        except Exception as e:
            log(f"Error during update: {e}")
            
        # Sleep for a random interval
        sleep_time = random.randint(MIN_INTERVAL, MAX_INTERVAL)
        log(f"Sleeping for {sleep_time // 60}m {sleep_time % 60}s...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    auto_push_loop()