from app.indexing.elasticsearch_handler import ElasticsearchHandler
from app.indexing.vector_store import VectorStore
from app.search.query_parser import QueryParser
from app.search.ranker import RankingStrategy
from app.search.snippet_generator import SnippetGenerator
from app.models.article import SearchResult, Article
from app.crawlers.crawler_manager import CrawlerManager
from rank_bm25 import BM25Okapi
import time
from datetime import datetime


class SearchService:
    def __init__(self):
        self.es_handler = ElasticsearchHandler()
        self.vector_store = VectorStore()
        self.query_parser = QueryParser()
        self.ranker = RankingStrategy()
        self.snippet_gen = SnippetGenerator()
        self.crawler = CrawlerManager()
        self.bm25_index = None

    def index_articles(self, articles: list[Article]):
        embeddings = self.vector_store.embed_batch(
            [f"{article.title} {article.excerpt}" for article in articles]
        )
        
        self.es_handler.bulk_index(articles, embeddings)
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

        bm25_results = self.es_handler.bm25_search(clean_query, top_k=top_k*2, filters=filters)
        
        if not bm25_results and clean_query:
            return {"error": "No results found"}

        query_embedding = self.vector_store.embed_text(clean_query)
        semantic_results = self.es_handler.semantic_search(query_embedding, top_k=top_k*2, filters=filters)

        merged_results = self._merge_results(bm25_results, semantic_results)

        bm25_scores = [r.get("_score", 0) for r in bm25_results[:len(merged_results)]]
        semantic_scores = [self._calculate_semantic_score(r, query_embedding) for r in merged_results]

        ranked_results = self.ranker.rank(merged_results, bm25_scores, semantic_scores)

        if sort_by == "recent":
            ranked_results.sort(key=lambda x: x[0].get("published_at", ""), reverse=True)
        elif sort_by == "trending":
            trending = self.get_trending_topics()
            ranked_results = self.ranker.boost_trending(ranked_results, trending)

        search_results = []
        for result, score in ranked_results[:top_k]:
            snippet = self.snippet_gen.generate(result.get("content", ""), clean_query)
            
            search_result = SearchResult(
                id=result["id"],
                title=result["title"],
                excerpt=result["excerpt"],
                snippet=snippet,
                url=result["url"],
                source=result["source"],
                author=result["author"],
                published_at=datetime.fromisoformat(result["published_at"]) if isinstance(result["published_at"], str) else result["published_at"],
                views=result.get("views", 0),
                likes=result.get("likes", 0),
                relevance_score=bm25_scores[0] if bm25_scores else 0,
                semantic_score=semantic_scores[0] if semantic_scores else 0,
                ranking_score=score,
                tags=result.get("tags", [])
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

    def _merge_results(self, bm25_results: list[dict], semantic_results: list[dict]) -> list[dict]:
        seen_ids = set()
        merged = []

        for result in bm25_results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                merged.append(result)

        for result in semantic_results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                merged.append(result)

        return merged

    def _calculate_semantic_score(self, result: dict, query_embedding: list[float]) -> float:
        result_embedding = result.get("embedding", [])
        if not result_embedding:
            return 0.5

        import numpy as np
        dot_product = np.dot(query_embedding, result_embedding)
        return float(dot_product)

    def get_trending_topics(self, days: int = 7) -> list[str]:
        try:
            agg_query = {
                "query": {
                    "range": {
                        "published_at": {
                            "gte": f"now-{days}d"
                        }
                    }
                },
                "aggs": {
                    "trending_tags": {
                        "terms": {"field": "tags", "size": 10}
                    }
                },
                "size": 0
            }

            results = self.es_handler.client.search(index=self.es_handler.index_name, body=agg_query)
            return [bucket["key"] for bucket in results["aggregations"]["trending_tags"]["buckets"]]
        except Exception as e:
            print(f"Error getting trending topics: {e}")
            return []

    def crawl_and_index_fresh(self, limit_per_source: int = 20):
        articles = self.crawler.fetch_all_sources(limit_per_source=limit_per_source)
        unique_articles = self.crawler.deduplicate_articles(articles)
        self.index_articles(unique_articles)
        return len(unique_articles)