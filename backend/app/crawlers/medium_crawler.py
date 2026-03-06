import requests
from bs4 import BeautifulSoup
from app.models.article import Article, ArticleSource
from datetime import datetime, timedelta
import json


class MediumCrawler:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.session = requests.Session()

    def fetch_tag_stories(self, tag: str = "technology", limit: int = 30) -> list[Article]:
        articles = []
        
        try:
            url = f"https://medium.com/tag/{tag}"
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Medium fetch error: {e}")
            return articles

        try:
            soup = BeautifulSoup(response.content, "html.parser")
            scripts = soup.find_all("script", {"type": "application/json"})
            
            for script in scripts:
                if "payload" in script.string:
                    data = json.loads(script.string)
                    if "initialState" in data:
                        articles.extend(self._parse_medium_payload(data, limit - len(articles)))
                    
                    if len(articles) >= limit:
                        break
        except Exception as e:
            print(f"Error parsing Medium content: {e}")

        return articles[:limit]

    def _parse_medium_payload(self, data: dict, limit: int) -> list[Article]:
        articles = []
        
        try:
            initial_state = data.get("initialState", {})
            for key, value in initial_state.items():
                if "Post" in key or "post" in key:
                    if isinstance(value, dict):
                        for post_id, post in value.items():
                            if len(articles) >= limit:
                                break
                            
                            article = self._parse_medium_post(post)
                            if article:
                                articles.append(article)
        except Exception as e:
            print(f"Error parsing Medium payload: {e}")

        return articles

    def _parse_medium_post(self, post: dict) -> Article:
        try:
            return Article(
                id=f"medium_{post.get('id', 'unknown')}",
                title=post.get("title", ""),
                content=post.get("content", {}).get("subtitle", ""),
                excerpt=post.get("content", {}).get("subtitle", "")[:200],
                url=f"https://medium.com/@{post.get('creator', {}).get('username', '')}/{post.get('uniqueSlug', '')}",
                source=ArticleSource.MEDIUM,
                author=post.get("creator", {}).get("name", "Unknown"),
                author_followers=post.get("creator", {}).get("socialStats", {}).get("followerCount", 0),
                published_at=datetime.fromtimestamp(post.get("firstPublishedAt", 0) / 1000),
                updated_at=datetime.fromtimestamp(post.get("updatedAt", 0) / 1000) if post.get("updatedAt") else None,
                views=post.get("readingTime", 0) * 10,
                likes=post.get("clapCount", 0) if "clapCount" in post else 0,
                comments=post.get("responsesCount", 0),
                tags=post.get("tags", [])
            )
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error parsing Medium post: {e}")
            return None