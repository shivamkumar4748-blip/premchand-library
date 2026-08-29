import feedparser
import requests
import json
import os

# Archive.org RSS Feed for Premchand Books
RSS_URL = "https://archive.org/advancedsearch.php?q=creator%3A%28Premchand%29+AND+mediatype%3A%28texts%29&rows=500&output=rss"

def run():
    print("Fetching Archive.org RSS feed...")
    feed = feedparser.parse(RSS_URL)
    
    print(f"Total books found: {len(feed.entries)}")
    
    if feed.entries:
        entry = feed.entries[0]
        print(f"Sample Book Title: {entry.title}")
        print(f"Sample Book Link: {entry.link}")

if __name__ == "__main__":
    run()
