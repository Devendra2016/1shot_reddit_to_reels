# README

## 1shot_reddit_to_reels

A Python automation tool to download top Reddit gaming clips, convert them for vertical reels, and upload them to Instagram with auto-commented hashtags.

---

## Requirements

- Python 3.8 or higher
- FFmpeg (must be installed and available in your system PATH)
- [pip](https://pip.pypa.io/en/stable/installation/)

### Python Packages

Install all dependencies with:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, use:

```bash
pip install instagrapi python-dotenv python-slugify yt-dlp praw
```

---

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Devendra2016/1shot_reddit_to_reels.git
   cd 1shot_reddit_to_reels
   ```

2. **Create a `.env` file** in the project root with your credentials:
   ```
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   REDDIT_USER_AGENT=your_user_agent
   OUTPUT_VIDEO_DIR=ready_to_post
   ```

3. **Create a `subreddits` file** in the project root, listing subreddit names separated by commas (e.g.):
   ```
   codwarzone,apexlegends,valorant
   ```

4. **Ensure FFmpeg is installed and in your PATH.**
   - [Download FFmpeg](https://ffmpeg.org/download.html) and follow platform-specific instructions.

---

## Usage

### 1. Download Reddit Videos

Run:
```bash
python reddit.py
```
- Downloads top videos from subreddits listed in `subreddits`.
- Saves them to `downloaded_videos/`.
- Logs details in `video_log.csv`.

### 2. Convert Videos for Reels

Run:
```bash
python enhance_cli.py
```
- Converts `.mp4` files to vertical format with blurred backgrounds.
- Saves processed videos to `ready_to_post/`.

### 3. Upload to Instagram

Run:
```bash
python insta.py
```
- Uploads up to 3 new videos per run from `ready_to_post/`.
- Posts hashtags as the first comment.
- Logs uploads in `upload_log.csv`.

---

## File Structure

```
.
├── reddit.py          # Reddit video downloader
├── enhance_cli.py     # Video formatting script
├── insta.py           # Instagram uploader with auto-comment
├── subreddits         # List of subreddits
├── .env               # Credentials and config
├── video_log.csv      # Download log
├── upload_log.csv     # Upload log
├── downloaded_videos/ # Raw videos
├── ready_to_post/     # Processed videos
└── requirements.txt   # Python dependencies
```

---

## Notes

- Do not share your `.env` file or credentials.
- Instagram may limit uploads if you post too frequently.
- For best results, run each script in order: `reddit.py` → `enhance_cli.py` → `insta.py`.

---
