import os
import subprocess
import logging
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor, as_completed

# -------------------- Load Environment Variables --------------------
load_dotenv()

# -------------------- Logging Setup --------------------
logging.basicConfig(
    filename='formatting.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_console(msg, level='info'):
    print(msg)
    getattr(logging, level)(msg)

# -------------------- Folders --------------------
input_dir = os.getenv("INPUT_VIDEO_DIR", "downloaded_videos")
output_dir = os.getenv("OUTPUT_VIDEO_DIR", "ready_to_post")

# -------------------- FFmpeg Filter for Blurred Background --------------------
filters = (
    "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
    "crop=1080:1920,boxblur=10:10[bg];"
    "[bg][fg]overlay=(W-w)/2:(H-h)/2"
)

# -------------------- Video Processing Function --------------------
def process_video(input_path, output_path):
    try:
        logging.info(f"🎬 Formatting: {os.path.basename(input_path)} → vertical with blur")
        cmd = f'ffmpeg -y -i "{input_path}" -filter_complex "{filters}" -c:a copy "{output_path}"'
        subprocess.run(cmd, check=True, shell=True)
        logging.info(f"✅ Saved to: {output_path}")

        with open("video_format_log.csv", "a", encoding="utf-8") as log_file:
            log_file.write(f"{input_path},{output_path}\n")

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ FFmpeg failed on {input_path}: {e}")

# -------------------- Main Function with Process Pool --------------------
MAX_WORKERS = 4

def main():
    if not os.path.exists("video_format_log.csv"):
        with open("video_format_log.csv", "w", encoding="utf-8") as log_file:
            log_file.write("Input Path,Output Path\n")

    tasks = []

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for subreddit_folder in os.listdir(input_dir):
            subreddit_path = os.path.join(input_dir, subreddit_folder)
            if not os.path.isdir(subreddit_path):
                continue

            output_subdir = os.path.join(output_dir, subreddit_folder)
            os.makedirs(output_subdir, exist_ok=True)

            for file in os.listdir(subreddit_path):
                if file.lower().endswith(".mp4"):
                    input_path = os.path.join(subreddit_path, file)
                    base_name = os.path.splitext(file)[0]
                    output_path = os.path.join(output_subdir, f"{base_name}_vertical.mp4")
                    tasks.append(executor.submit(process_video, input_path, output_path))

        for task in as_completed(tasks):
            try:
                task.result()
            except Exception as e:
                logging.error(f"❌ Unhandled exception: {e}")

    log_console("\n🏁 All videos processed.")

if __name__ == "__main__":
    main()