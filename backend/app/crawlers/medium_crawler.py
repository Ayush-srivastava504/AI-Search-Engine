import requests
from app.models.article import Article, ArticleSource
from datetime import datetime
from typing import Optional

class MediumCrawler:
    def __init__(self):
        self.base_url = "https://medium.com"
        self.api_url = "https://api.rss2json.com/v1/api.json"
        self.session = requests.Session()

    def fetch_tag_stories(self, tag: str = "technology", limit: int = 30) -> list[Article]:
        try:
            params = {
                "rss_url": f"{self.base_url}/feed/tag/{tag}"
            }
            response = self.session.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for item in data.get("items", [])[:limit]:
                article = self._parse_rss_item(item)
                if article:
                    articles.append(article)
            return articles
            
        except Exception as e:
            print(f"Medium API error: {e}")
            return []

    def _parse_rss_item(self, item: dict) -> Optional[Article]:
        try:
            return Article(
                id=f"medium_{item.get('guid', 'unknown')}",
                title=item.get("title", ""),
                content=item.get("description", ""),
                excerpt=item.get("description", "")[:200],
                url=item.get("link", ""),
                source=ArticleSource.MEDIUM,
                author=item.get("author", "Unknown"),
                author_followers=0,
                published_at=datetime.fromisoformat(item.get("pubDate", "2024-01-01").replace("Z", "+00:00")),
                views=0,
                likes=0,
                comments=0,
                tags=[]
            )
        except Exception as e:
            print(f"Error parsing Medium RSS item: {e}")
            return None