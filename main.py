import os
import feedparser

BLOG_ID = os.environ.get("BLOG_ID")

def fetch_archive_books():
    print("Fetching Archive.org RSS feed...")
    rss_url = "https://archive.org/advancedsearch.php?q=creator%3A%22Premchand%22+AND+mediatype%3A%22texts%22&rows=500&output=rss"
    feed = feedparser.parse(rss_url)
    return feed.entries

def run():
    entries = fetch_archive_books()
    print(f"Total books found: {len(entries)}")
    
    if entries:
        entry = entries[0]
        print(f"Sample Book Title: {entry.title}")
        print(f"Sample Book Link: {entry.link}")
        print(f"Target Blogger ID: {BLOG_ID}")

if __name__ == "__main__":
    run()
