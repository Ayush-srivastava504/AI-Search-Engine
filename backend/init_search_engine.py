#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.crawlers.crawler_manager import CrawlerManager
from app.search.search_service import SearchService


async def main():
    print(" Initializing Tech Articles Search Engine...")
    
    print("\n Initializing search service...")
    search_service = SearchService()
    
    print("\n Crawling articles from multiple sources...")
    print("   - Dev.to API")
    print("   - Hacker News API")
    print("   - Medium")
    
    articles = search_service.crawler.fetch_all_sources(limit_per_source=30)
    unique_articles = search_service.crawler.deduplicate_articles(articles)
    
    print(f"\n Found {len(unique_articles)} unique articles")
    
    if unique_articles:
        print("\n Indexing articles...")
        search_service.index_articles(unique_articles)
        print(f" Successfully indexed {len(unique_articles)} articles")
    
    print("\n Getting trending topics...")
    trending = search_service.get_trending_topics()
    if trending:
        print(f" Trending: {', '.join(trending[:5])}")
    
    print("\n Search engine is ready!")
    print("\n Start the server with:")
    print("   python backend/app/main.py")
    print("\n API Documentation:")
    print("   http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())