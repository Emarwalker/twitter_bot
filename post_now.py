import os, random, tweepy, re, string
from dotenv import load_dotenv

load_dotenv()  # สำหรับรันในเครื่อง; บน Actions ใช้ Secrets

# v2 client (โพสต์ทวีต)
client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET"),
)

# v1.1 api (อัปโหลดรูป)
auth = tweepy.OAuth1UserHandler(
    os.getenv("API_KEY"),
    os.getenv("API_SECRET"),
    os.getenv("ACCESS_TOKEN"),
    os.getenv("ACCESS_SECRET"),
)
api_v1 = tweepy.API(auth)

TWEETS_FILE = "tweets.txt"
ASSETS_DIR = "assets"
MAX_LEN = 280

# ---------- helper: random code ----------
def gen_code() -> str:
    letters = "".join(random.choice(string.ascii_uppercase) for _ in range(2))
    digits  = "".join(random.choice(string.digits) for _ in range(2))
    return letters + digits

PLACEHOLDER_PATTERN = re.compile(
    r"\(\((?:CODE|RAND4|ภาษาอังกฤษ 2 ตัวเลขอีก สอง|รหัส4|ENG2NUM2)\)\)",
    flags=re.IGNORECASE,
)

def pick_post(path: str):
    """อ่านโพสต์แบบคั่นด้วย --- และดึงไฟล์รูปถ้ามี (IMG: filename)
       พร้อมแทนที่ placeholder ด้วยรหัสแบบ AB12
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    posts = [p.strip() for p in content.split("---") if p.strip()]
    if not posts:
        raise RuntimeError("tweets.txt is empty or missing '---' separators")

    post = random.choice(posts)
    code = gen_code()

    # หาไฟล์รูปจากบรรทัด IMG:
    img = None
    m = re.search(r"^IMG:\s*(.+)$", post, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        img = m.group(1).strip()
        # ตัดบรรทัด IMG: ออกไม่ให้ไปโพสต์ในข้อความ
        post = re.sub(r"^IMG:\s*.+$", "", post, flags=re.IGNORECASE | re.MULTILINE).strip()

    # แทนที่ placeholder ถ้ามี
    if PLACEHOLDER_PATTERN.search(post):
        post = PLACEHOLDER_PATTERN.sub(code, post)
    else:
        # ถ้าไม่มี placeholder ให้เติมรหัสไว้ท้ายข้อความ (ก่อนตัดความยาว)
        post = f"{post}\n{code}"

    return post[:MAX_LEN], img  # (ข้อความ, ชื่อรูปหรือ None)

def upload_media_if_any(filename: str | None):
    if not filename:
        return None
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.isfile(path):
        print(f"⚠️ ไม่พบรูป: {path} — โพสต์เป็นข้อความอย่างเดียว")
        return None
    media = api_v1.media_upload(filename=path)
    return media.media_id

if __name__ == "__main__":
    try:
        text, img_name = pick_post(TWEETS_FILE)
        media_id = upload_media_if_any(img_name)
        if media_id:
            client.create_tweet(text=text, media_ids=[media_id])
        else:
            client.create_tweet(text=text)
        print("✅ Posted:", text, f"(image={img_name})")
    except Exception as e:
        print("❌ Error:", e)
        raise
