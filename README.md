# 1shot_reddit_to_reels

A complete automation pipeline to download top Reddit gaming clips, convert them for vertical reels, and upload them to Instagram with auto-commented hashtags.  
This project is ideal for gaming content creators who want to streamline their short-form video workflow.

---

## Features

- **One-command pipeline:** Run all steps (download, format, upload) with a single command.
- **Live logging:** See progress and errors in real time.
- **Dependency checks:** Warns you if any required Python packages are missing.
- **Windows encoding fix:** Automatically sets UTF-8 encoding for smooth operation on Windows.
- **Modular scripts:** Each step (download, format, upload) is a separate script for easy customization.

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
pip install praw yt-dlp python-slugify python-dotenv instagrapi psutil tqdm
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

### Run the full pipeline

Just run:

```bash
python main.py
```

This will:
1. Download top videos from subreddits listed in `subreddits` (`reddit.py`)
2. Convert videos to vertical format for reels (`enhance_cli.py`)
3. Upload videos to Instagram with hashtags as the first comment (`insta.py`)

All steps are logged live to your console.

---

## File Structure

```
.
├── main.py             # Pipeline runner with live logging and dependency checks
├── reddit.py           # Reddit video downloader
├── enhance_cli.py      # Video formatting script
├── insta.py            # Instagram uploader with auto-comment
├── subreddits          # List of subreddits
├── .env                # Credentials and config
├── video_log.csv       # Download log
├── upload_log.csv      # Upload log
├── downloaded_videos/  # Raw videos
├── ready_to_post/      # Processed videos
└── requirements.txt    # Python dependencies
```

---

## Notes

- Do not share your `.env` file or credentials.
- Instagram may limit uploads if you post too frequently.
- For best results, run the pipeline periodically (e.g., once per day).

---

## License

MIT License (see [LICENSE](LICENSE))

---



https://github.com/user-attachments/assets/16307008-0d4f-4308-aaa6-c2be85c5e758


