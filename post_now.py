import os, random, tweepy
from dotenv import load_dotenv

load_dotenv()  # local dev; on Actions use secrets

client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET"),
)

TWEETS_FILE = "tweets.txt"
MAX_LEN = 280

def pick_tweet(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    posts = [p.strip() for p in content.split("---") if p.strip()]
    if not posts:
        raise RuntimeError("tweets.txt is empty or missing '---' separators")
    return random.choice(posts)[:MAX_LEN]

if __name__ == "__main__":
    text = pick_tweet(TWEETS_FILE)
    client.create_tweet(text=text)
    print("✅ Posted:\n", text)
