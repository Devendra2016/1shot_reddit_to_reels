import os
import praw
import yt_dlp
import logging
import threading
from queue import Queue
from slugify import slugify
from dotenv import load_dotenv

# -------------------- Load Environment Variables --------------------
load_dotenv()

# -------------------- Logging Setup --------------------
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_console(msg, level='info'):
    print(msg)
    getattr(logging, level)(msg)

# -------------------- Reddit API Setup --------------------
client_id = os.getenv('REDDIT_CLIENT_ID')
client_secret = os.getenv('REDDIT_CLIENT_SECRET')
user_agent = os.getenv('REDDIT_USER_AGENT')

if not all([client_id, client_secret, user_agent]):
    log_console("❗ Missing Reddit API credentials in environment variables.", 'error')
    exit(1)

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

# -------------------- Read Subreddits --------------------
with open("subreddits", "r", encoding="utf-8") as f:
    content = f.read()
subreddits = [s.strip() for s in content.split(',') if s.strip()]
if not subreddits:
    log_console("❗ No valid subreddits found in subreddits.txt", 'error')
    exit(1)
else:
    log_console(f"🔍 Found {len(subreddits)} subreddits: {subreddits}")

# -------------------- CSV Log Setup --------------------
log_file = "video_log.csv"
if not os.path.exists(log_file):
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("Subreddit,Title,Reddit URL\n")

# -------------------- Threading Setup --------------------
MAX_THREADS = 5
download_queue = Queue()
log_lock = threading.Lock()

def download_post_video(subreddit_name, post, output_dir, log_file):
    try:
        if post.is_video and getattr(post, 'media', None):
            title_slug = slugify(post.title)[:100]
            filename = os.path.join(output_dir, f"{title_slug}.mp4")
            reddit_url = f"https://reddit.com{post.permalink}"

            if os.path.exists(filename):
                log_console(f"🔁 Skipping (already exists): {title_slug}")
                return

            log_console(f"\n⬇️ Downloading from r/{subreddit_name}: {post.title}")
            log_console(f"🔗 Source URL: {post.url}")

            ydl_opts = {
                'outtmpl': filename,
                'quiet': True,
                'noplaylist': True,
                'merge_output_format': 'mp4',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([post.url])
            log_console(f"✅ Downloaded: {filename}")

            with log_lock:
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"{subreddit_name},\"{post.title}\",{reddit_url}\n")

    except Exception as e:
        log_console(f"❌ Thread exception in '{threading.current_thread().name}': {e}", 'error')

def worker():
    while True:
        item = download_queue.get()
        if item is None:
            break
        try:
            subreddit_name, post, output_dir, log_file = item
            log_console(f"🔧 Worker processing: {post.title}")
            download_post_video(subreddit_name, post, output_dir, log_file)
        except Exception as e:
            log_console(f"❌ Error in worker thread: {e}", 'error')
        finally:
            download_queue.task_done()

# -------------------- Main Logic --------------------
threads = []
for _ in range(MAX_THREADS):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

for subreddit_name in subreddits:
    output_dir = os.path.join("downloaded_videos", slugify(subreddit_name))
    if not os.path.exists(output_dir):
        log_console(f"📁 Creating output directory for r/{subreddit_name}: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    log_console(f"\n🏷️ Processing r/{subreddit_name} (top this week)")
    subreddit = reddit.subreddit(subreddit_name)
    try:
        posts = subreddit.top(time_filter="week", limit=10)
    except Exception as e:
        log_console(f"❌ Failed to fetch posts for r/{subreddit_name}: {e}", 'error')
        continue

    for post in posts:
        download_queue.put((subreddit_name, post, output_dir, log_file))

# Wait for all tasks to complete
download_queue.join()

# Stop all workers
for _ in range(MAX_THREADS):
    download_queue.put(None)
for t in threads:
    t.join()

log_console("\nAll done. Enjoy your downloaded reels! 🕹️🎬")
