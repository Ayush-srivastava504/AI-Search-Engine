import requests
from app.models.article import Article, ArticleSource
from datetime import datetime
from app.config import settings


class HackerNewsCrawler:
    def __init__(self):
        self.base_url = settings.hackernews_api_url
        self.session = requests.Session()

    def fetch_top_stories(self, limit: int = 30) -> list[Article]:
        try:
            response = self.session.get(f"{self.base_url}/topstories.json", timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:limit]
        except requests.RequestException as e:
            print(f"HN API error: {e}")
            return []

        articles = []
        for story_id in story_ids:
            try:
                item_response = self.session.get(f"{self.base_url}/item/{story_id}.json", timeout=5)
                item_response.raise_for_status()
                item = item_response.json()

                if item.get("type") != "story" or not item.get("url"):
                    continue

                article = Article(
                    id=f"hn_{item['id']}",
                    title=item.get("title", ""),
                    content=item.get("title", ""),
                    excerpt=item.get("title", "")[:200],
                    url=item.get("url", ""),
                    source=ArticleSource.HACKERNEWS,
                    author=item.get("by", "Anonymous"),
                    author_followers=0,
                    published_at=datetime.fromtimestamp(item.get("time", 0)),
                    views=item.get("score", 0),
                    likes=item.get("score", 0),
                    comments=item.get("descendants", 0),
                    tags=["hackernews"]
                )
                articles.append(article)
            except requests.RequestException as e:
                print(f"Error fetching HN item {story_id}: {e}")
                continue
            except (KeyError, ValueError) as e:
                print(f"Error parsing HN article: {e}")
                continue

        return articles

    def fetch_best_stories(self, limit: int = 30) -> list[Article]:
        try:
            response = self.session.get(f"{self.base_url}/beststories.json", timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:limit]
        except requests.RequestException as e:
            print(f"HN API error: {e}")
            return []

        articles = []
        for story_id in story_ids:
            try:
                item_response = self.session.get(f"{self.base_url}/item/{story_id}.json", timeout=5)
                item_response.raise_for_status()
                item = item_response.json()

                if item.get("type") != "story" or not item.get("url"):
                    continue

                article = Article(
                    id=f"hn_{item['id']}",
                    title=item.get("title", ""),
                    content=item.get("title", ""),
                    excerpt=item.get("title", "")[:200],
                    url=item.get("url", ""),
                    source=ArticleSource.HACKERNEWS,
                    author=item.get("by", "Anonymous"),
                    author_followers=0,
                    published_at=datetime.fromtimestamp(item.get("time", 0)),
                    views=item.get("score", 0),
                    likes=item.get("score", 0),
                    comments=item.get("descendants", 0),
                    tags=["hackernews", "best"]
                )
                articles.append(article)
            except requests.RequestException as e:
                print(f"Error fetching HN item {story_id}: {e}")
                continue
            except (KeyError, ValueError) as e:
                print(f"Error parsing HN article: {e}")
                continue

        return articles