# --- START OF FILE insta.py (with Auto-Commenting) ---

import os
import time
import random
import logging
import csv
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from slugify import slugify

# --- Setup ---
load_dotenv()
logging.basicConfig(
    filename='upload.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def log_console(msg, level='info'):
    print(msg)
    getattr(logging, level)(msg)

IG_USERNAME = os.getenv("INSTAGRAM_USERNAME")
IG_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
SESSION_FILE = "ig_session.json"
INPUT_VIDEO_DIR = os.getenv("OUTPUT_VIDEO_DIR", "ready_to_post")
DOWNLOAD_LOG = "video_log.csv"
UPLOAD_LOG = "upload_log.csv"
MAX_UPLOADS_PER_RUN = 3

# --- ADJUSTED TIMING (Average 3 mins, High Risk) ---
MIN_DELAY_MINUTES = 10
MAX_DELAY_MINUTES = 15
# ----------------------------------------------------

# --- Game-Specific Content ---
GAME_SPECIFIC_DATA = {
    'codwarzone': {'captions': ["Sending them to the Gulag. 💀", "Just another day in Urzikstan."], 'hashtags': ['warzone', 'codwarzone', 'callofduty', 'warzoneclips']},
    'apexlegends': {'captions': ["This is what peak Apex looks like.", "Becoming the Apex Champion."], 'hashtags': ['apexlegends', 'apex', 'apexlegendsclips', 'playapex']},
    'valorant': {'captions': ["One-tap machine activated.", "That's an ACE!"], 'hashtags': ['valorant', 'valorantclips', 'riotgames', 'playvalorant']},
    'globaloffensive': {'captions': ["RUSH B, DON'T STOP!", "That flick was disrespectful."], 'hashtags': ['csgo', 'cs2', 'counterstrike', 'csgoclips']},
    'overwatch': {'captions': ["PLAY OF THE GAME!", "Witness the perfect ultimate."], 'hashtags': ['overwatch', 'overwatch2', 'ow2', 'potg']},
    'escapefromtarkov': {'captions': ["Head, Eyes. The Tarkov special.", "Cheeki Breeki!"], 'hashtags': ['escapefromtarkov', 'tarkov', 'eft', 'tarkovclips']},
    'halo': {'captions': ["Finish the fight. Spartan style.", "Overkill!"], 'hashtags': ['halo', 'haloinfinite', 'masterchief', 'haloclips']},
    'destinythegame': {'captions': ["Eyes up, Guardian.", "The Traveler would be proud."], 'hashtags': ['destiny2', 'destinythegame', 'bungie', 'guardian']},
    'thefinalsthegame': {'captions': ["CASH OUT SUCCESSFUL!", "This game is pure chaos."], 'hashtags': ['thefinals', 'thefinalsgame', 'embarkstudios', 'thefinalsclips']},
    'xdefiant': {'captions': ["Dominated the lobby.", "Classic arcade shooter vibes."], 'hashtags': ['xdefiant', 'xdefiantgame', 'ubisoft', 'newfps']},
    'default': {'captions': ["Wait for it... 😂", "You can't make this up.", "This is reel-y good."], 'hashtags': ['reels', 'viral', 'explorepage', 'trending']}
}

cl = Client()

def login_to_instagram():
    if not all([IG_USERNAME, IG_PASSWORD]):
        log_console("❗ Missing INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD in .env file.", 'error')
        exit(1)
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(IG_USERNAME, IG_PASSWORD)
            cl.get_timeline_feed()
            log_console("✅ Logged in successfully using session file.")
            return True
        except Exception as e:
            log_console(f"Could not reuse session: {e}. Re-logging in.", 'warning')
    try:
        cl.login(IG_USERNAME, IG_PASSWORD)
        cl.dump_settings(SESSION_FILE)
        log_console("✅ Logged in successfully and created new session file.")
        return True
    except Exception as e:
        log_console(f"❌ Failed to log in to Instagram: {e}", 'error')
        return False

def generate_caption(title, subreddit):
    subreddit_key = subreddit.lower()
    game_data = GAME_SPECIFIC_DATA.get(subreddit_key, GAME_SPECIFIC_DATA['default'])
    intro = random.choice(game_data['captions'])
    return (
        f"{intro}\n\n"
        f"🎬: {title.strip()}\n\n"
        f"Follow for more daily clips! 💎"
    )

def generate_hashtags(subreddit):
    subreddit_key = subreddit.lower()
    game_data = GAME_SPECIFIC_DATA.get(subreddit_key, GAME_SPECIFIC_DATA['default'])
    final_hashtags = set(game_data['hashtags'] + GAME_SPECIFIC_DATA['default']['hashtags'])
    return " ".join(f"#{tag}" for tag in final_hashtags)

def get_uploaded_videos():
    if not os.path.exists(UPLOAD_LOG): return set()
    uploaded = set()
    try:
        with open(UPLOAD_LOG, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row: uploaded.add(row[1])
    except StopIteration: pass
    return uploaded

def load_video_metadata():
    if not os.path.exists(DOWNLOAD_LOG):
        log_console(f"❌ Download log '{DOWNLOAD_LOG}' not found. Please run reddit.py first.", "error")
        return None
    metadata = {}
    try:
        with open(DOWNLOAD_LOG, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            if "Subreddit" not in header:
                log_console(f"❌ Corrupted '{DOWNLOAD_LOG}'. Missing 'Subreddit' column. Delete it and run reddit.py again.", "error")
                return None
            idx_subreddit, idx_title = header.index("Subreddit"), header.index("Title")
            for row in reader:
                if len(row) > max(idx_subreddit, idx_title):
                    title = row[idx_title]
                    slug = slugify(title, max_length=100)
                    metadata[slug] = {"title": title, "subreddit": row[idx_subreddit]}
    except StopIteration:
        log_console(f"'{DOWNLOAD_LOG}' is empty.", "warning")
    return metadata

def main():
    if not login_to_instagram(): return

    video_metadata = load_video_metadata()
    if video_metadata is None: return

    uploaded_paths = get_uploaded_videos()
    videos_to_upload = []

    for subdir, _, files in os.walk(INPUT_VIDEO_DIR):
        for file in files:
            if file.lower().endswith("_vertical.mp4"):
                full_path = os.path.join(subdir, file)
                if full_path not in uploaded_paths: videos_to_upload.append(full_path)
    
    if not videos_to_upload:
        log_console("✅ No new videos to upload. All synced!")
        return
    
    log_console(f"Found {len(videos_to_upload)} new videos to post. Will upload up to {MAX_UPLOADS_PER_RUN}.")
    
    uploads_this_run = 0
    random.shuffle(videos_to_upload)

    for video_path in videos_to_upload:
        if uploads_this_run >= MAX_UPLOADS_PER_RUN:
            log_console(f"Reached upload limit for this run ({MAX_UPLOADS_PER_RUN}).")
            break

        video_slug = os.path.basename(video_path).replace("_vertical.mp4", "")
        video_info = video_metadata.get(video_slug)
        
        if not video_info:
            log_console(f"⚠️ Could not find metadata for slug '{video_slug}'. Skipping.", "warning")
            continue

        title, subreddit = video_info['title'], video_info['subreddit']
        log_console(f"\n🚀 Preparing to upload: {title} (from r/{subreddit})")
        
        # --- THIS IS THE CRITICAL CHANGE ---
        # 1. Generate caption and hashtags separately
        caption_text = generate_caption(title, subreddit)
        hashtags_text = generate_hashtags(subreddit)
        
        try:
            log_console(f"📤 Uploading '{video_path}' to Instagram as a Reel...")
            
            # 2. Upload the clip with only the caption and get the media object back
            media = cl.clip_upload(
                path=video_path,
                caption=caption_text
            )
            
            # Log successful upload to prevent re-uploading
            with open(UPLOAD_LOG, "a", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), video_path])
            
            log_console(f"✅ Successfully uploaded! ✨")
            
            # 3. Add a short, human-like pause before commenting
            comment_delay = random.randint(5, 15)
            log_console(f"🕒 Pausing for {comment_delay} seconds before commenting...")
            time.sleep(comment_delay)

            # 4. Post the hashtags as the first comment
            comment = cl.media_comment(media_id=media.pk, text=hashtags_text)
            if comment:
                log_console(f"✍️ Successfully posted hashtags in the first comment.")
            else:
                log_console(f"⚠️ Failed to post hashtags as a comment.", "warning")

            uploads_this_run += 1

            # Wait before the next UPLOAD
            if uploads_this_run < MAX_UPLOADS_PER_RUN and len(videos_to_upload) > uploads_this_run:
                delay = random.randint(MIN_DELAY_MINUTES * 60, MAX_DELAY_MINUTES * 60)
                log_console(f"🕒 Waiting for {delay // 60} minutes and {delay % 60} seconds before next upload...")
                time.sleep(delay)

        except Exception as e:
            log_console(f"❌ Upload or comment failed for {video_path}: {e}", "error")

    log_console("\n🏁 Instagram upload run finished.")

if __name__ == "__main__":
    main()