import os
import smtplib
import feedparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
BLOGGER_EMAIL = os.environ.get("BLOGGER_SECRET_EMAIL")

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
        print(f"✅ Email sent successfully for: {title}")
    except Exception as e:
        print(f"❌ Failed to send email for '{title}': {str(e)}")

def run():
    if not SENDER_EMAIL or not SENDER_PASSWORD or not BLOGGER_EMAIL:
        print("Missing required environment secrets: SENDER_EMAIL, SENDER_PASSWORD, or BLOGGER_SECRET_EMAIL.")
        return

    print("Fetching Hindi books from Archive.org...")
    rss_url = "https://archive.org/advancedsearch.php?q=mediatype%3A(texts)%20AND%20language%3A(hindi)&sort[]=date+desc&rows=10&output=rss"
    feed = feedparser.parse(rss_url)

    print(f"Total entries fetched: {len(feed.entries)}")

    count = 0
    for entry in feed.entries:
        title = getattr(entry, 'title', 'Hindi Book')
        link = getattr(entry, 'link', '#')
        summary = getattr(entry, 'summary', 'No summary provided.')

        body = f"""
        <p><b>विवरण:</b> {summary}</p>
        <hr/>
        <p>📖 <a href="{link}" target="_blank">इंटरनेट आर्काइव पर पढ़ें / डाउनलोड करें</a></p>
        """
        send_post_via_email(title, body)
        
        count += 1
        if count >= 3:  # Testing with 3 books
            break

if __name__ == "__main__":
    run()
