import feedparser
from datetime import datetime, timedelta
import time

ISLAM_RSS_FEEDS = [
    "https://www.aljazeera.com/xml/rss/all.xml",
    # Add more RSS feeds if needed
]

def fetch_islamic_rss():
    articles = []
    now = datetime.utcnow()
    two_days_ago = now - timedelta(days=2)

    for feed_url in ISLAM_RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                print(f"No entries found in: {feed_url}")
                continue

            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                image_url = None

                # Try to extract image from media tags or summary
                if "media_content" in entry:
                    image_url = entry.media_content[0].get("url")
                elif "media_thumbnail" in entry:
                    image_url = entry.media_thumbnail[0].get("url")
                elif "enclosures" in entry and entry.enclosures:
                    image_url = entry.enclosures[0].get("href")
                else:
                    # Try to parse <img> from summary HTML
                    import re
                    match = re.search(r'<img.*?src=["\'](.*?)["\']', summary)
                    if match:
                        image_url = match.group(1)

                # Parse publish date
                try:
                    published = entry.published_parsed
                    if not published:
                        print(f"Missing published_parsed in entry: {title}")
                        continue
                    published_dt = datetime.fromtimestamp(time.mktime(published))
                    if published_dt < two_days_ago:
                        continue
                except Exception as e:
                    print(f"Date parse failed for: {title}\nError: {e}")
                    continue

                articles.append({
                    "title": title,
                    "description": summary,
                    "url": link,
                    "image": image_url,
                    "published": published_dt.strftime("%Y-%m-%d %H:%M")
                })

        except Exception as e:
            print(f"Error fetching from {feed_url}:\n{e}")
            continue

    return articles
