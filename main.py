import os
import json
import feedparser
from google.oauth2 import service_account
from googleapiclient.discovery import build

BLOG_ID = os.environ.get("BLOGGER_BLOG_ID")
SA_KEY_JSON = os.environ.get("GCP_SA_KEY")

def get_blogger_service():
    # Blogger full control scope
    scopes = ['https://www.googleapis.com/auth/blogger']
    
    # Parse JSON Secret directly
    sa_info = json.loads(SA_KEY_JSON)
    
    # Load credentials directly from Service Account key
    creds = service_account.Credentials.from_service_account_info(
        sa_info, 
        scopes=scopes
    )
    
    return build('blogger', 'v3', credentials=creds)

def post_to_blogger(service, title, link, summary):
    html_content = f"""
    <p><b>पुस्तक विवरण:</b> {summary}</p>
    <hr/>
    <p>
        📖 <a href="{link}" target="_blank">इंटरनेट आर्काइव पर पढ़ें / डाउनलोड करें</a>
    </p>
    """
    body = {
        "title": title,
        "content": html_content
    }

    try:
        posts = service.posts()
        # Direct API call using Service Account
        request = posts.insert(blogId=BLOG_ID, body=body, isDraft=True)
        response = request.execute()
        print(f"✅ Successfully posted to Draft: {title}")
    except Exception as e:
        print(f"❌ Failed to post '{title}': {str(e)}")

def fetch_archive_books():
    print("Fetching Hindi books from Archive.org...")
    rss_uri = "https://archive.org/advancedsearch.php?q=mediatype%3A(texts)%20AND%20language%3A(hindi)&sort[]=date+desc&rows=10&output=rss"
    feed = feedparser.parse(rss_uri)
    return feed.entries

def run():
    if not SA_KEY_JSON or not BLOG_ID:
        print("Missing required secrets: GCP_SA_KEY or BLOGGER_BLOG_ID.")
        return

    try:
        service = get_blogger_service()
        entries = fetch_archive_books()
        print(f"Total entries fetched: {len(entries)}")

        count = 0
        for entry in entries:
            title = getattr(entry, 'title', 'Hindi Book')
            link = getattr(entry, 'link', '#')
            summary = getattr(entry, 'summary', 'No summary provided.')
            
            post_to_blogger(service, title, link, summary)
            count += 1
            if count >= 3: # Testing with 3 books
                break

    except Exception as err:
        print(f"Execution failed: {str(err)}")

if __name__ == "__main__":
    run()
