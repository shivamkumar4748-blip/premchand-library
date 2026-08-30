import os
import smtplib
import feedparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
BLOGGER_EMAIL = os.environ.get("BLOGGER_SECRET_EMAIL")

STATE_FILE = "posted.txt"

def load_posted():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_posted(link):
    with open(STATE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{link}\n")

def send_post_via_email(title, content):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = BLOGGER_EMAIL
    msg['Subject'] = title

    msg.attach(MIMEText(content, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, BLOGGER_EMAIL, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        return False

def run():
    if not SENDER_EMAIL or not SENDER_PASSWORD or not BLOGGER_EMAIL:
        print("Missing required environment secrets.")
        return

    print("Fetching Hindi books from Archive.org...")
    # rows=500 करने से पूरी 313 बुक्स फ़ेच होंगी
    rss_url = "https://archive.org/advancedsearch.php?q=mediatype%3A(texts)%20AND%20language%3A(hindi)&sort[]=date+desc&rows=500&output=rss"
    feed = feedparser.parse(rss_url)

    total_books = len(feed.entries)
    posted_links = load_posted()

    # जो बुक्स अभी तक पोस्ट नहीं हुई हैं
    unposted = [entry for entry in feed.entries if getattr(entry, 'link', '') not in posted_links]
    already_done = total_books - len(unposted)

    print(f"\n==========================================")
    print(f"📊 PROGRESS UPDATE:")
    print(f"✔ Completed: {already_done} / {total_books}")
    print(f"⏳ Pending: {len(unposted)} books")
    print(f"==========================================\n")

    if not unposted:
        print("🎉 ऑल बुक्स पब्लिश हो चुकी हैं!")
        return

    # इस रन में सिर्फ 1 बुक भेजेंगे
    entry = unposted[0]
    title = getattr(entry, 'title', 'Hindi Book')
    link = getattr(entry, 'link', '#')
    summary = getattr(entry, 'summary', 'No summary provided.')

    current_num = already_done + 1
    remaining_after = len(unposted) - 1

    body = f"""
    <p><b>विवरण:</b> {summary}</p>
    <hr/>
    <p>📖 <a href="{link}" target="_blank">इंटरनेट आर्काइव पर पढ़ें / डाउनलोड करें</a></p>
    <br/>
    <hr/>
    <small style="color: gray;">🤖 <b>Auto-Post Status:</b> Book {current_num} of {total_books} | Remaining: {remaining_after}</small>
    """

    if send_post_via_email(title, body):
        save_posted(link)
        print(f"✅ Successfully posted: {title}")
        print(f"📊 Status Updated: {current_num}/{total_books} Done | {remaining_after} Pending")
    else:
        print("❌ Error sending email. State not updated.")

if __name__ == "__main__":
    run()
