import os
import requests
import feedparser

BLOG_ID = os.environ.get("BLOGGER_BLOG_ID")
CLIENT_ID = os.environ.get("BLOGGER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("BLOGGER_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("BLOGGER_REFRESH_TOKEN")

def get_access_token():
    """Direct Google Auth Endpoint से फ्रेश Access Token लेता है"""
    url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=payload)
    data = response.json()
    if "access_token" not in data:
        print(f"Token Error: {data}")
        return None
    return data["access_token"]

def post_to_blogger(access_token, title, link, summary):
    """Direct REST API endpoint से पोस्ट पब्लिश/ड्राफ्ट करता है"""
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts?isDraft=true"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    html_content = f"""
    <p><img src="{link}" alt="{title}" /></p>
    <p>{summary}</p>
    <ul>
        <li><b>लेखक:</b> Internet Archive</li>
        <li><b>भाषा:</b> हिंदी</li>
    </ul>
    <p>
        <a href="{link}" target="_blank">Read Online</a> | 
        <a href="{link}" target="_blank">Download PDF</a>
    </p>
    """

    body = {
        "title": title,
        "content": html_content
    }

    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code == 200:
        print(f"Successfully saved to Draft: {title}")
    else:
        print(f"Failed to post {title}: {response.status_code} - {response.text}")

def fetch_archive_books():
    print("Fetching Archive.org RSS feed...")
    rss_uri = "https://archive.org/advancedsearch.php?q=mediatype%3A(texts)%20AND%20language%3A(hindi)&sort[]=date+desc&rows=50&output=rss"
    feed = feedparser.parse(rss_uri)
    return feed.entries

def run():
    access_token = get_access_token()
    if not access_token:
        print("Failed to acquire access token. Stopping.")
        return

    entries = fetch_archive_books()
    print(f"Total books found in feed: {len(entries)}")

    if not entries:
        print("No entries found.")
        return

    new_books_added = 0
    for entry in entries:
        title = getattr(entry, 'title', 'Untitled Book')
        link = getattr(entry, 'link', '#')
        summary = getattr(entry, 'summary', 'No description available.')
            
        print(f"Processing new book: {title}")
        post_to_blogger(access_token, title, link, summary)
        new_books_added += 1
        
        if new_books_added >= 5: 
            break

if __name__ == "__main__":
    run()
