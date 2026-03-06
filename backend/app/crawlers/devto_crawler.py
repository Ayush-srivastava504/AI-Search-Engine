import requests
from app.models.article import Article, ArticleSource
from datetime import datetime
from app.config import settings


class DevtoCrawler:
    def __init__(self):
        self.api_url = settings.devto_api_url
        self.session = requests.Session()

    def fetch_articles(self, page: int = 1, per_page: int = 30) -> list[Article]:
        params = {
            "page": page,
            "per_page": per_page,
            "sort": "-published_at"
        }
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"Dev.to API error: {e}")
            return []

        articles = []
        for item in data:
            try:
                article = Article(
                    id=f"devto_{item['id']}",
                    title=item["title"],
                    content=item.get("body_markdown", ""),
                    excerpt=item.get("description", "")[:200],
                    url=item["url"],
                    source=ArticleSource.DEVTO,
                    author=item["user"]["name"],
                    author_followers=item["user"].get("followers_count", 0),
                    published_at=datetime.fromisoformat(item["published_at"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00")) if item.get("updated_at") else None,
                    views=item.get("positive_reactions_count", 0),
                    likes=item.get("positive_reactions_count", 0),
                    comments=item.get("comments_count", 0),
                    tags=item.get("tags", []),
                    image_url=item.get("cover_image")
                )
                articles.append(article)
            except (KeyError, ValueError) as e:
                print(f"Error parsing Dev.to article: {e}")
                continue

        return articles

    def fetch_by_tag(self, tag: str, page: int = 1, per_page: int = 30) -> list[Article]:
        params = {
            "tag": tag,
            "page": page,
            "per_page": per_page
        }
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"Dev.to API error: {e}")
            return []

        articles = []
        for item in data:
            try:
                article = Article(
                    id=f"devto_{item['id']}",
                    title=item["title"],
                    content=item.get("body_markdown", ""),
                    excerpt=item.get("description", "")[:200],
                    url=item["url"],
                    source=ArticleSource.DEVTO,
                    author=item["user"]["name"],
                    author_followers=item["user"].get("followers_count", 0),
                    published_at=datetime.fromisoformat(item["published_at"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00")) if item.get("updated_at") else None,
                    views=item.get("positive_reactions_count", 0),
                    likes=item.get("positive_reactions_count", 0),
                    comments=item.get("comments_count", 0),
                    tags=item.get("tags", []),
                    image_url=item.get("cover_image")
                )
                articles.append(article)
            except (KeyError, ValueError) as e:
                print(f"Error parsing Dev.to article: {e}")
                continue

        return articles