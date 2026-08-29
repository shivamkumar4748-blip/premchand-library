import os
import feedparser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = os.environ.get("BLOG_ID")
CLIENT_ID = os.environ.get("GCP_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GCP_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")

def get_blogger_service():
    """Google Blogger API के लिए 인증 (Authentication) तैयार करता है"""
    credentials = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/blogger"]
    )
    return build("blogger", "v3", credentials=credentials)

def fetch_archive_books():
    print("Fetching Archive.org RSS feed...")
    rss_url = "https://archive.org/advancedsearch.php?q=creator%3A%22Premchand%22+AND+mediatype%3A%22texts%22&rows=500&output=rss"
    feed = feedparser.parse(rss_url)
    return feed.entries

def post_to_blogger(service, title, link):
    """ब्लॉगर पर नई पोस्ट पब्लिश करता है"""
    try:
        body = {
            "title": title,
            "content": f"<p>Premchand Book Title: {title}</p><p>Read/Download from Archive.org: <a href='{link}'>{link}</a></p>"
        }
        posts = service.posts()
        request = posts.insert(blogId=BLOG_ID, body=body)
        response = request.execute()
        print(f"Successfully posted: {title} (Post ID: {response.get('id')})")
    except Exception as e:
        print(f"Failed to post {title}: {e}")

def run():
    entries = fetch_archive_books()
    print(f"Total books found: {len(entries)}")
    
    if not entries:
        print("No entries found.")
        return

    # ब्लॉगर सर्विस कनेक्ट करें
    service = get_blogger_service()

    # फिलहाल टेस्टिंग के लिए पहली किताब पोस्ट करके देखते हैं
    entry = entries[0]
    print(f"Sample Book Title: {entry.title}")
    print(f"Sample Book Link: {entry.link}")
    print(f"Target Blogger ID: {BLOG_ID}")
    
    # ब्लॉगर पर पोस्ट करने के लिए नीचे की लाइन अनकमेंट करें:
    # post_to_blogger(service, entry.title, entry.link)

if __name__ == "__main__":
    run()
