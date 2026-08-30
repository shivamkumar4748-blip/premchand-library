import feedparser
import html
import datetime

def generate_blogger_xml():
    print("Fetching 500 Hindi books from Archive.org...")
    rss_url = "https://archive.org/advancedsearch.php?q=mediatype%3A(texts)%20AND%20language%3A(hindi)&sort[]=date+desc&rows=500&output=rss"
    feed = feedparser.parse(rss_url)

    entries_xml = ""
    post_id = 1000

    for entry in feed.entries:
        post_id += 1
        title = html.escape(getattr(entry, 'title', 'Hindi Book'))
        link = html.escape(getattr(entry, 'link', '#'))
        summary = html.escape(getattr(entry, 'summary', 'No summary available.'))
        
        published = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        content_html = html.escape(f"<div><p><b>विवरण:</b> {summary}</p><hr/><p>📖 <a href='{link}'>पढ़ें / डाउनलोड करें</a></p></div>")

        entry_template = f"""
  <entry>
    <id>tag:blogger.com,1999:blog-1.post-{post_id}</id>
    <published>{published}</published>
    <updated>{published}</updated>
    <category scheme="http://schemas.google.com/g/2005#kind" term="http://schemas.google.com/b/2007#kind#post"/>
    <title type="text">{title}</title>
    <content type="html">{content_html}</content>
    <app:control xmlns:app="http://purl.org/atom/app#">
      <app:draft>yes</app:draft>
    </app:control>
  </entry>"""
        entries_xml += entry_template

    full_xml = f"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom' xmlns:openSearch='http://a9.com/-/spec/opensearch/1.1/' xmlns:blogger='http://schemas.google.com/blogger/2008'>
  <title type='text'>Archive Hindi Books Bulk Import</title>
  {entries_xml}
</feed>"""

    with open("blogger_import.xml", "w", encoding="utf-8") as f:
        f.write(full_xml)

    print(f"✅ SUCCESS: Saved {len(feed.entries)} books into blogger_import.xml")

if __name__ == "__main__":
    generate_blogger_xml()
