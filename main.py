import os
import smtplib
import feedparser
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
BLOGGER_SECRET_EMAIL = os.environ.get("BLOGGER_SECRET_EMAIL")

STATE_FILE = "posted.txt"

def clean_title(title):
    clean = re.sub(r'[^\w\s\u0900-\u097F]', '', title)
    return clean.strip()[:100]

def load_posted():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_posted(link):
    with open(STATE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{link}\n")

def send_via_direct_tunnel(title, content):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = clean_title(title)
    msg['From'] = f"Shivam Thakur <{SENDER_EMAIL}>"
    msg['To'] = BLOGGER_SECRET_EMAIL
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid(domain='gmail.com')
    
    # Bypass Headers - Google Filter Bypass
    msg['X-Mailer'] = 'Thunderbird/115.0'
    msg['X-Priority'] = '3'
    
    part_html = MIMEText(content, 'html', 'utf-8')
    msg.attach(part_html)

    # PORT 465 SSL Direct Tunnel Engine
    context = smtplib.ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, BLOGGER_SECRET_EMAIL, msg.as_string())

def run():
    if not SENDER_EMAIL or not SENDER_PASSWORD or not BLOGGER_SECRET_EMAIL:
        print("❌ Secrets missing!")
        return

    print("Fetching Hindi books from Archive.org...")
    rss_url = "https://archive.org/advancedsearch.php?q=mediatype%3A(texts)%20AND%20language%3A(hindi)&sort[]=date+desc&rows=500&output=rss"
    feed = feedparser.parse(rss_url)

    total_books = len(feed.entries)
    posted_links = load_posted()

    unposted = [entry for entry in feed.entries if getattr(entry, 'link', '') not in posted_links]
    already_done = total_books - len(unposted)

    print(f"\n==========================================")
    print(f"📊 PROGRESS UPDATE:")
    print(f"✔ Completed: {already_done} / {total_books}")
    print(f"⏳ Pending: {len(unposted)} books")
    print(f"==========================================\n")

    if not unposted:
        print("🎉 सभी किताबें प्रोसेस हो चुकी हैं!")
        return

    entry = unposted[0]
    title = getattr(entry, 'title', 'Hindi Book')
    link = getattr(entry, 'link', '#')
    summary = getattr(entry, 'summary', 'No summary provided.')

    body_html = f"""
    <div style="font-family: Arial, sans-serif;">
        <p><b>विवरण:</b> {summary}</p>
        <hr/>
        <p>📖 <a href="{link}">इंटरनेट आर्काइव पर पढ़ें / डाउनलोड करें</a></p>
    </div>
    """

    try:
        send_via_direct_tunnel(title, body_html)
        save_posted(link)
        print(f"✅ Tunnel Delivery Successful: {title}")
        print(f"📊 Updated: {already_done + 1}/{total_books} Done")
    except Exception as e:
        print(f"❌ Tunnel Blocked: {str(e)}")

if __name__ == "__main__":
    run()
