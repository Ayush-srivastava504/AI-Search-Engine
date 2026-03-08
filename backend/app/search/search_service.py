from app.search.query_parser import QueryParser
from app.search.snippet_generator import SnippetGenerator
from app.models.article import SearchResult, Article
from app.crawlers.crawler_manager import CrawlerManager
from rank_bm25 import BM25Okapi
import time
from datetime import datetime


class SearchService:
    def __init__(self):
        self.query_parser = QueryParser()
        self.snippet_gen = SnippetGenerator()
        self.crawler = CrawlerManager()
        self.documents = {}
        self.bm25 = None
        self.doc_list = []

    def index_articles(self, articles: list[Article]):
        self.documents = {article.id: article for article in articles}
        self.doc_list = articles
        
        contents = [f"{article.title} {article.content} {' '.join(article.tags)}" for article in articles]
        tokenized = [content.lower().split() for content in contents]
        
        self.bm25 = BM25Okapi(tokenized)
        print(f"Indexed {len(articles)} articles")

    def hybrid_search(self, query: str, top_k: int = 10, sort_by: str = "relevance") -> dict:
        start_time = time.time()

        parsed_query = self.query_parser.parse(query)
        clean_query = parsed_query["clean_query"]

        filters = {}
        if parsed_query["site"]:
            filters["source"] = parsed_query["site"]
        if parsed_query["author"]:
            filters["author"] = parsed_query["author"]
        if parsed_query["from_date"]:
            filters["from_date"] = parsed_query["from_date"]
        if parsed_query["to_date"]:
            filters["to_date"] = parsed_query["to_date"]

        if not self.bm25 or not self.doc_list:
            return {"error": "No documents indexed"}

        tokenized_query = clean_query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k*2]
        
        filtered_results = []
        for idx in top_indices:
            if idx < len(self.doc_list):
                doc = self.doc_list[idx]
                
                if filters.get("source") and doc.source.value != filters["source"]:
                    continue
                if filters.get("author") and doc.author.lower() != filters["author"].lower():
                    continue
                
                filtered_results.append((idx, doc, scores[idx]))

        if not filtered_results:
            return {"error": "No results found"}

        if sort_by == "recent":
            filtered_results.sort(key=lambda x: x[1].published_at, reverse=True)
        elif sort_by == "trending":
            trending = self.get_trending_topics()
            filtered_results.sort(key=lambda x: (
                any(tag in trending for tag in x[1].tags),
                x[2]
            ), reverse=True)

        search_results = []
        for idx, doc, score in filtered_results[:top_k]:
            snippet = self.snippet_gen.generate(doc.content, clean_query)
            
            search_result = SearchResult(
                id=doc.id,
                title=doc.title,
                excerpt=doc.excerpt,
                snippet=snippet,
                url=doc.url,
                source=doc.source,
                author=doc.author,
                published_at=doc.published_at,
                views=doc.views,
                likes=doc.likes,
                relevance_score=float(score),
                semantic_score=0.0,
                ranking_score=float(score),
                tags=doc.tags
            )
            search_results.append(search_result)

        execution_time = (time.time() - start_time) * 1000

        return {
            "query": query,
            "filters_applied": filters,
            "total_results": len(search_results),
            "results": search_results,
            "execution_time_ms": execution_time
        }

    def get_trending_topics(self, days: int = 7) -> list[str]:
        if not self.doc_list:
            return []
        
        tag_counts = {}
        for doc in self.doc_list:
            for tag in doc.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, count in sorted_tags[:10]]

    def crawl_and_index_fresh(self, limit_per_source: int = 20):
        articles = self.crawler.fetch_all_sources(limit_per_source=limit_per_source)
        unique_articles = self.crawler.deduplicate_articles(articles)
        self.index_articles(unique_articles)
        return len(unique_articles)
