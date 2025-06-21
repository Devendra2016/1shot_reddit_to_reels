# --- START OF FILE enhance_cli.py (Assertive CPU Logic) ---

import os
import subprocess
import logging
import csv
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil
from tqdm import tqdm

# -------------------- Load Environment Variables --------------------
load_dotenv()

# -------------------- Logging Setup --------------------
logging.basicConfig(
    filename='formatting.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(processName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_console(msg, level='info'):
    print(msg)
    getattr(logging, level)(msg)

# -------------------- Folders --------------------
INPUT_DIR = os.getenv("INPUT_VIDEO_DIR", "downloaded_videos")
OUTPUT_DIR = os.getenv("OUTPUT_VIDEO_DIR", "ready_to_post")
FORMAT_LOG_FILE = "video_format_log.csv"

# -------------------- Definitive 'Blurred Background' FFmpeg Filter --------------------
FFMPEG_FILTERS = (
    "[0:v]split=2[original][background];"
    "[background]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:15[blurred_bg];"
    "[original]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
    "[blurred_bg][fg]overlay=(W-w)/2:(H-h)/2"
)

# -------------------- Video Processing Function --------------------
def process_video(input_path, output_path):
    try:
        cmd = (
            f'ffmpeg -y -i "{input_path}" -filter_complex "{FFMPEG_FILTERS}" -aspect 9:16 '
            f'-c:v libx264 -preset faster -crf 23 -c:a copy -loglevel error "{output_path}"'
        )
        subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return (input_path, output_path)
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ FFmpeg failed on {os.path.basename(input_path)}.")
        logging.error(f"   Command: {e.cmd}")
        logging.error(f"   Stderr: {e.stderr}")
        return None
    except Exception as e:
        logging.error(f"❌ An unexpected error occurred while processing {os.path.basename(input_path)}: {e}")
        raise

# -------------------- State Management --------------------
def get_already_formatted_videos():
    if not os.path.exists(FORMAT_LOG_FILE):
        with open(FORMAT_LOG_FILE, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Input Path", "Output Path"])
        return set()
    
    formatted_videos = set()
    try:
        with open(FORMAT_LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row:
                    formatted_videos.add(row[0])
    except (IOError, StopIteration):
        pass
    return formatted_videos

# -------------------- Main Function --------------------
def main():
    if not os.path.exists(INPUT_DIR):
        log_console(f"❗ Input directory '{INPUT_DIR}' not found. Please run reddit.py first.", 'error')
        return

    already_formatted = get_already_formatted_videos()
    tasks_to_run = []

    log_console(f"🔍 Scanning for new videos in '{INPUT_DIR}' to format...")
    
    for subreddit_folder in os.listdir(INPUT_DIR):
        subreddit_path = os.path.join(INPUT_DIR, subreddit_folder)
        if not os.path.isdir(subreddit_path):
            continue

        output_subdir = os.path.join(OUTPUT_DIR, subreddit_folder)
        os.makedirs(output_subdir, exist_ok=True)

        for file in os.listdir(subreddit_path):
            if file.lower().endswith(".mp4"):
                input_path = os.path.join(subreddit_path, file)
                if input_path in already_formatted:
                    continue

                base_name = os.path.splitext(file)[0]
                output_path = os.path.join(output_subdir, f"{base_name}_vertical.mp4")
                tasks_to_run.append((input_path, output_path))

    if not tasks_to_run:
        log_console("✅ All videos have already been formatted. Nothing to do.")
        return

    log_console(f"Found {len(tasks_to_run)} new videos to format.")

    # --- THIS IS THE CRITICAL CHANGE ---
    # This logic now ignores the current CPU load and just uses a fixed percentage of total cores.
    cpu_count = os.cpu_count() or 4 # Get total cores, default to 4 if undetectable
    # Use 75% of the total cores, with a minimum of 1 and a max of 12 (to prevent overkill on servers)
    max_workers = min(12, max(1, int(cpu_count * 0.75)))
    log_console(f"🧠 Using an assertive strategy with up to {max_workers} worker processes.")
    # ------------------------------------

    processed_count = 0
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {executor.submit(process_video, task[0], task[1]): task[0] for task in tasks_to_run}
        
        pbar = tqdm(as_completed(future_to_path), total=len(tasks_to_run), desc="Formatting Videos", unit="video")

        for future in pbar:
            path = future_to_path[future]
            try:
                result = future.result()
                if result:
                    with open(FORMAT_LOG_FILE, "a", encoding="utf-8", newline='') as log_file:
                        writer = csv.writer(log_file)
                        writer.writerow(result)
                    processed_count += 1
            except Exception as e:
                log_console(f"❌ A task for {os.path.basename(path)} generated an exception: {e}", 'error')

    log_console(f"\n🏁 Formatting complete. Successfully formatted {processed_count}/{len(tasks_to_run)} new videos.")

if __name__ == "__main__":
    main()