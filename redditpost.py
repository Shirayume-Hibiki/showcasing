import praw
from datetime import datetime, timezone
reddit_client_id = "FkvHtjOh6cCfH9-TaJqk_A"
reddit_client_secret = "mf8uDYs_Q-k1QpGbO7NLK85VIIMGrg"

def get_subreddit_text(subreddit_name="cryptomarkets"):
    reddit = praw.Reddit(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        redirect_uri="http://localhost:8001",
        user_agent="testscript 1.0",
    )

    text_result = ''
    subreddit = reddit.subreddit(subreddit_name)

    for submission in subreddit.hot(limit=10):
        text_result += submission.title + "\n" + submission.selftext + "\n"

    return text_result

def main():
    text_reddit = get_subreddit_text(subreddit_name="CryptoMarkets")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    output_cont = f"=== Data fetched at: {timestamp} (GMT+0) ===\n\n{text_reddit}"
    print(output_cont)
    with open('redditpostarchive.txt', 'w', encoding='utf-8') as f:
        f.write(output_cont)
if __name__ == "__main__":
    main()
