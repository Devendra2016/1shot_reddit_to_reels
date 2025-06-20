# --- START OF FILE main.py (Live Logging Version) ---

import subprocess
import sys
import time
import os
import importlib.util

# --- Dependency Check ---
def check_dependencies():
    """Checks if essential libraries are installed."""
    print("Checking for required libraries...")
    required_packages = {
        "praw": "for reddit.py",
        "yt_dlp": "for reddit.py",
        "slugify": "for reddit.py",
        "psutil": "for enhance_cli.py",
        "tqdm": "for enhance_cli.py",
        "instagrapi": "for insta.py"
    }
    missing = []
    for package, reason in required_packages.items():
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing.append((package, reason))
    
    if missing:
        print("\n❌ FATAL ERROR: Missing required Python libraries.")
        for package, reason in missing:
            print(f"  - Package '{package}' is missing ({reason}).")
        print("\nPlease install them by running:")
        print(f"  pip install {' '.join([p[0] for p in missing])}")
        return False
        
    print("✅ All required libraries are installed.")
    return True


# --- Windows Encoding Fix ---
if os.name == 'nt' and os.environ.get('PYTHONIOENCODING', '') != 'UTF-8':
    print("Windows environment detected. Setting PYTHONIOENCODING to UTF-8 and restarting...")
    os.environ['PYTHONIOENCODING'] = 'UTF-8'
    try:
        subprocess.run([sys.executable] + sys.argv, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    sys.exit(0)

def print_header(title):
    """Prints a styled header to the console."""
    print("\n" + "="*60)
    print(f"====== {title.upper():^48} ======")
    print("="*60 + "\n")

def run_script_live(script_name):
    """
    Runs a Python script and streams its output live.
    Returns True on success, False on failure.
    """
    try:
        # We don't capture_output here, allowing the child process to print directly
        # to the console in real-time.
        process = subprocess.run(
            [sys.executable, script_name],
            check=True  # This will raise CalledProcessError if the script fails
        )
        return True
    except FileNotFoundError:
        print(f"\n❌ FATAL ERROR: The script '{script_name}' was not found.")
        print("Please make sure all scripts (reddit.py, enhance_cli.py, insta.py) are in the same directory.")
        return False
    except subprocess.CalledProcessError as e:
        # The error message from the script would have already been printed to the console.
        # We just need to add our own context.
        print(f"\n❌ FATAL ERROR: The script '{script_name}' failed with return code {e.returncode}.")
        return False
    except Exception as e:
        print(f"\n❌ An unexpected error occurred while trying to run '{script_name}': {e}")
        return False

def main():
    """
    Main function to run the entire Reddit-to-Reels pipeline.
    """
    start_time = time.time()
    
    print_header("Initializing Pipeline")

    if not check_dependencies():
        return

    # --- Step 1: Download videos from Reddit ---
    print_header("Step 1: Downloading Videos from Reddit")
    if not run_script_live("reddit.py"):
        print("\nPipeline stopped due to an error in the download step.")
        return
    print("\n✅ Step 1 completed successfully.")

    # --- Step 2: Format videos for vertical view ---
    print_header("Step 2: Formatting Videos for Reels")
    if not run_script_live("enhance_cli.py"):
        print("\nPipeline stopped due to an error in the formatting step.")
        return
    print("\n✅ Step 2 completed successfully.")
    
    # --- Step 3: Upload videos to Instagram ---
    print_header("Step 3: Uploading Videos to Instagram")
    if not run_script_live("insta.py"):
        print("\nPipeline stopped due to an error in the upload step.")
        return
    print("\n✅ Step 3 completed successfully.")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print_header("Pipeline Finished")
    print(f"🎉 All steps completed successfully in {duration:.2f} seconds.")
    print("Check your Instagram account for new reels! 🥳")

if __name__ == "__main__":
    main()