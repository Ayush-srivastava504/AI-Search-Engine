from elasticsearch import Elasticsearch
from app.models.article import Article
from app.config import settings


class ElasticsearchHandler:
    def __init__(self):
        self.client = Elasticsearch(settings.elasticsearch_host)
        self.index_name = "tech-articles"
        self._create_index_if_not_exists()

    def _create_index_if_not_exists(self):
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(
                index=self.index_name,
                settings={
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "analyzer": {
                            "standard_analyzer": {
                                "type": "standard",
                                "stopwords": "_english_"
                            }
                        }
                    }
                },
                mappings={
                    "properties": {
                        "title": {
                            "type": "text",
                            "analyzer": "standard_analyzer",
                            "fields": {"keyword": {"type": "keyword"}}
                        },
                        "content": {
                            "type": "text",
                            "analyzer": "standard_analyzer"
                        },
                        "excerpt": {
                            "type": "text",
                            "analyzer": "standard_analyzer"
                        },
                        "url": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "author": {"type": "keyword"},
                        "author_followers": {"type": "integer"},
                        "published_at": {"type": "date"},
                        "updated_at": {"type": "date"},
                        "views": {"type": "integer"},
                        "likes": {"type": "integer"},
                        "comments": {"type": "integer"},
                        "tags": {"type": "keyword"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 384,
                            "index": True,
                            "similarity": "cosine"
                        }
                    }
                }
            )

    def index_article(self, article: Article, embedding: list[float]):
        doc = {
            **article.model_dump(exclude={"embedding"}),
            "embedding": embedding,
            "published_at": article.published_at.isoformat()
        }

        self.client.index(
            index=self.index_name,
            id=article.id,
            document=doc
        )

    def bulk_index(self, articles: list[Article], embeddings: list[list[float]]):
        operations = []

        for article, embedding in zip(articles, embeddings):
            operations.append({
                "index": {
                    "_index": self.index_name,
                    "_id": article.id
                }
            })

            doc = {
                **article.model_dump(exclude={"embedding"}),
                "embedding": embedding,
                "published_at": article.published_at.isoformat()
            }

            operations.append(doc)

        self.client.bulk(operations=operations)

    def bm25_search(self, query: str, top_k: int = 10, filters: dict | None = None) -> list[dict]:

        es_query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title", "content", "excerpt"],
                            "fuzziness": "AUTO"
                        }
                    }
                ],
                "filter": []
            }
        }

        if filters:
            if filters.get("source"):
                es_query["filter"].append({"term": {"source": filters["source"]}})

            if filters.get("author"):
                es_query["filter"].append({"term": {"author": filters["author"]}})

        results = self.client.search(
            index=self.index_name,
            query=es_query,
            size=top_k
        )

        docs = []

        for hit in results["hits"]["hits"]:
            doc = hit["_source"]
            doc["ranking_score"] = hit["_score"]
            docs.append(doc)

        return docs

    def semantic_search(self, embedding: list[float], top_k: int = 10, filters: dict | None = None) -> list[dict]:

        es_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": embedding}
                }
            }
        }

        results = self.client.search(
            index=self.index_name,
            query=es_query,
            size=top_k
        )

        docs = []

        for hit in results["hits"]["hits"]:
            doc = hit["_source"]
            doc["ranking_score"] = hit["_score"]
            docs.append(doc)

        return docs

    def get_all_tags(self) -> list[str]:

        results = self.client.search(
            index=self.index_name,
            size=0,
            aggs={
                "unique_tags": {
                    "terms": {
                        "field": "tags",
                        "size": 100
                    }
                }
            }
        )

        return [bucket["key"] for bucket in results["aggregations"]["unique_tags"]["buckets"]]