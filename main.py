import os
import feedparser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = os.environ.get("BLOG_ID")
CLIENT_ID = os.environ.get("GCP_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GCP_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")

def get_blogger_service():
    """Google Blogger API कनेक्शन तैयार करता है"""
    credentials = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/blogger"]
    )
    return build("blogger", "v3", credentials=credentials)

def get_existing_posts(service):
    """ब्लॉगर पर पहले से मौजूद सभी पोस्ट्स के टाइटल्स की लिस्ट निकालता है ताकि डुप्लीकेट न आए"""
    existing_titles = set()
    try:
        request = service.posts().list(blogId=BLOG_ID, status="live,draft", maxResults=500)
        while request:
            response = request.execute()
            for post in response.get("items", []):
                existing_titles.add(post.get("title"))
            request = service.posts().list_next(request, response)
    except Exception as e:
        print(f"Error fetching existing posts: {e}")
    return existing_titles

def fetch_archive_books():
    """इंटरनेट आर्काइव से एक बार में 50 किताबों की बड़ी फीड फेच करता है"""
    print("Fetching Archive.org RSS feed...")
    rss_uri = "https://archive.org/advancedsearch.php?q=mediatype%3A(texts)%20AND%20language%3A(hindi)&sort[]=date+desc&rows=50&output=rss"
    feed = feedparser.parse(rss_uri)
    return feed.entries

def post_to_blogger(service, title, link, summary):
    """तय किए गए HTML फॉर्मेट में किताब को सीधे ड्राफ्ट में भेजता है"""
    try:
        html_content = f"""
        <!-- 1. बुक कवर फोटो का direct link -->
        <p><img src="{link}" alt="{title}" /></p>
        
        <!-- 2. बुक का विवरण (Description) -->
        <p>{summary}</p>
        
        <!-- 3. महत्वपूर्ण जानकारी (Book Meta Details) -->
        <ul>
            <li><b>लेखक:</b> Internet Archive</li>
            <li><b>भाषा:</b> हिंदी</li>
        </ul>
        
        <!-- 4. ऑरिजिनल लिंक और डाउनलोड लिंक्स -->
        <p>
            <a href="{link}" target="_blank">Read Online</a> | 
            <a href="{link}" target="_blank">Download PDF</a>
        </p>
        """

        body = {
            "title": title,
            "content": html_content,
            "status": "DRAFT"
        }

        posts = service.posts()
        request = posts.insert(blogId=BLOG_ID, body=body, isDraft=True)
        response = request.execute()
        print(f"Successfully saved to Draft: {title}")
    
    except Exception as e:
        print(f"Failed to post {title}: {e}")

def run():
    service = get_blogger_service()
    existing_titles = get_existing_posts(service)
    
    entries = fetch_archive_books()
    print(f"Total books found in feed: {len(entries)}")

    if not entries:
        print("No entries found.")
        return

    # डुप्लीकेट चेक करते हुए केवल नई किताबें ड्राफ्ट में डाली जाएंगी
    new_books_added = 0
    for entry in entries:
        title = getattr(entry, 'title', 'Untitled Book')
        link = getattr(entry, 'link', '#')
        summary = getattr(entry, 'summary', 'No description available.')
        
        if title in existing_titles:
            print(f"Skipping duplicate: {title}")
            continue
            
        print(f"Processing new book: {title}")
        post_to_blogger(service, title, link, summary)
        new_books_added += 1
        
        # सुरक्षा के लिए प्रति रन लिमिट सेट की जा सकती है ताकि आराम से गैप मिले
        if new_books_added >= 5: 
            break

if __name__ == "__main__":
    run()
