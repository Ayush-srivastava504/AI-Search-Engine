from app.crawlers.devto_crawler import DevtoCrawler
from app.crawlers.hackernews_crawler import HackerNewsCrawler
from app.crawlers.medium_crawler import MediumCrawler
from app.models.article import Article
import asyncio
from concurrent.futures import ThreadPoolExecutor


class CrawlerManager:
    def __init__(self):
        self.devto = DevtoCrawler()
        self.hn = HackerNewsCrawler()
        self.medium = MediumCrawler()
        self.executor = ThreadPoolExecutor(max_workers=3)

    def fetch_all_sources(self, limit_per_source: int = 20) -> list[Article]:
        articles = []
        
        try:
            devto_articles = self.devto.fetch_articles(per_page=limit_per_source)
            articles.extend(devto_articles)
            print(f"Fetched {len(devto_articles)} articles from Dev.to")
        except Exception as e:
            print(f"Dev.to error: {e}")

        try:
            hn_articles = self.hn.fetch_top_stories(limit=limit_per_source)
            articles.extend(hn_articles)
            print(f"Fetched {len(hn_articles)} articles from Hacker News")
        except Exception as e:
            print(f"Hacker News error: {e}")

        try:
            medium_articles = self.medium.fetch_tag_stories(tag="technology", limit=limit_per_source)
            articles.extend(medium_articles)
            print(f"Fetched {len(medium_articles)} articles from Medium")
        except Exception as e:
            print(f"Medium error: {e}")

        return articles

    def fetch_by_tag(self, tag: str, limit_per_source: int = 15) -> list[Article]:
        articles = []
        
        try:
            devto_articles = self.devto.fetch_by_tag(tag, per_page=limit_per_source)
            articles.extend(devto_articles)
        except Exception as e:
            print(f"Dev.to tag fetch error: {e}")

        try:
            medium_articles = self.medium.fetch_tag_stories(tag=tag, limit=limit_per_source)
            articles.extend(medium_articles)
        except Exception as e:
            print(f"Medium tag fetch error: {e}")

        return articles

    def deduplicate_articles(self, articles: list[Article]) -> list[Article]:
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        return unique_articles