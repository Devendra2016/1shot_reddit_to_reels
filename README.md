# 1shot_reddit_to_reels

A Python tool to automatically download top Reddit gaming clips and reformat them for vertical, blurred-background reels—perfect for sharing on platforms like Instagram Reels, YouTube Shorts, and TikTok.

## Features

- **Multi-threaded Reddit video downloader**: Fetches top weekly posts from a list of subreddits and downloads their videos.
- **Automatic video formatting**: Uses FFmpeg to convert downloaded videos to vertical format with blurred backgrounds.
- **Logging**: Keeps logs of downloads and formatting in CSV and log files.
- **Configurable**: Easily set subreddits and environment variables.

## Requirements

- Python 3.8+
- FFmpeg (must be installed and available in your PATH)
- [praw](https://praw.readthedocs.io/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [python-slugify](https://github.com/un33k/python-slugify)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

Install dependencies:
```sh
pip install -r requirements.txt
```
*(Create `requirements.txt` with the following if not present: praw yt-dlp python-slugify python-dotenv)*

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/Devendra2016/1shot_reddit_to_reels.git
   cd 1shot_reddit_to_reels
   ```

2. **Configure Reddit API credentials:**
   - Create a `.env` file (see [.env](.env)) with:
     ```
     REDDIT_CLIENT_ID=your_client_id
     REDDIT_CLIENT_SECRET=your_client_secret
     REDDIT_USER_AGENT=your_user_agent
     ```

3. **Set your subreddits:**
   - Edit the [subreddits](subreddits) file, listing subreddit names separated by commas.

4. **Ensure FFmpeg is installed and in your system PATH.**

## Usage

### 1. Download Reddit Videos

Run:
```sh
python reddit.py
```
- Downloads top weekly videos from each subreddit in `subreddits`.
- Saves videos to `downloaded_videos/<subreddit>/`.
- Logs details in [video_log.csv](video_log.csv).

### 2. Convert Videos for Reels

Run:
```sh
python enhance_cli.py
```
- Converts all `.mp4` files in `downloaded_videos/` to vertical format with blurred backgrounds.
- Saves processed videos to `ready_to_post/<subreddit>/`.
- Logs formatting in [video_format_log.csv](video_format_log.csv).

## File Structure

```
.
├── reddit.py              # Reddit video downloader
├── enhance_cli.py         # Video formatting script
├── subreddits             # List of subreddits to process
├── .env                   # Reddit API credentials
├── video_log.csv          # Download log
├── video_format_log.csv   # Formatting log
├── downloaded_videos/     # Raw downloaded videos
├── ready_to_post/         # Processed, vertical videos
├── app.log                # Application log
├── formatting.log         # Formatting log
└── LICENSE
```

## License

[Apache 2.0](LICENSE)

---

*Made with ❤️ for gaming content creators!*
