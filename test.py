with open("subreddits", "r", encoding="utf-8") as f:
    subreddits = f.read().strip()
    for subreddit in subreddits.split(","):
        print(subreddit.strip())