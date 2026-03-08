import requests
from app.models.article import Article, ArticleSource
from datetime import datetime
from typing import Optional
import time
import feedparser

class DevtoCrawler:
    def __init__(self):
        self.api_url = "https://dev.to/api/articles"
        self.rss_url = "https://dev.to/feed"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def fetch_articles(self, page: int = 1, per_page: int = 30) -> list[Article]:
        articles = self._fetch_from_rss()
        if not articles:
            articles = self._fetch_from_api(page, per_page)
        return articles[:per_page]

    def fetch_by_tag(self, tag: str, page: int = 1, per_page: int = 30) -> list[Article]:
        tag_rss = f"https://dev.to/feed/tag/{tag}"
        articles = self._fetch_from_rss_url(tag_rss)
        if not articles:
            articles = self._fetch_from_api(page, per_page, tag)
        return articles[:per_page]

    def _fetch_from_rss(self) -> list[Article]:
        return self._fetch_from_rss_url(self.rss_url)

    def _fetch_from_rss_url(self, url: str) -> list[Article]:
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries:
                article = self._parse_rss_entry(entry)
                if article:
                    articles.append(article)
            
            if articles:
                print(f"Dev.to: Fetched {len(articles)} articles from RSS")
            return articles
            
        except Exception as e:
            print(f"Dev.to RSS error: {e}")
            return []

    def _parse_rss_entry(self, entry) -> Optional[Article]:
        try:
            author_name = entry.get("author", "Unknown")
            
            return Article(
                id=f"devto_{entry.get('id', entry.link.split('/')[-1])}",
                title=entry.get("title", ""),
                content=entry.get("summary", ""),
                excerpt=self._truncate(entry.get("summary", ""), 200),
                url=entry.get("link", ""),
                source=ArticleSource.DEVTO,
                author=author_name,
                author_followers=0,
                published_at=datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                views=0,
                likes=0,
                comments=0,
                tags=entry.get("tags", []) if hasattr(entry, 'tags') else [],
                image_url=None
            )
        except Exception as e:
            print(f"Error parsing Dev.to RSS entry: {e}")
            return None

    def _fetch_from_api(self, page: int = 1, per_page: int = 30, tag: Optional[str] = None) -> list[Article]:
        try:
            params = {
                "page": page,
                "per_page": min(per_page, 30)
            }
            if tag:
                params["tag"] = tag
            
            response = self.session.get(
                self.api_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                print(f"Dev.to: Fetched {len(data)} articles from API")
                return self._parse_articles(data)
            return []
            
        except Exception as e:
            print(f"Dev.to API error: {e}")
            return []

    def _parse_articles(self, data: list) -> list[Article]:
        articles = []
        for item in data:
            article = self._parse_article(item)
            if article:
                articles.append(article)
        return articles

    def _parse_article(self, item: dict) -> Optional[Article]:
        try:
            published_at_str = item["published_at"].replace("Z", "+00:00")
            
            return Article(
                id=f"devto_{item['id']}",
                title=item.get("title", ""),
                content=item.get("body_markdown", ""),
                excerpt=self._truncate(item.get("description", ""), 200),
                url=item.get("url", ""),
                source=ArticleSource.DEVTO,
                author=item.get("user", {}).get("name", "Unknown"),
                author_followers=item.get("user", {}).get("followers_count", 0),
                published_at=datetime.fromisoformat(published_at_str),
                views=item.get("positive_reactions_count", 0),
                likes=item.get("positive_reactions_count", 0),
                comments=item.get("comments_count", 0),
                tags=item.get("tag_list", []),
                image_url=item.get("cover_image")
            )
        except Exception as e:
            print(f"Error parsing Dev.to article: {e}")
            return None

    def _truncate(self, text: str, length: int) -> str:
        return text[:length] if text else ""