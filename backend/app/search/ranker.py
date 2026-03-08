from datetime import datetime, timedelta
import numpy as np

class RankingStrategy:
    def __init__(self):
        self.weights = {
            "relevance": 0.4,
            "authority": 0.2,
            "recency": 0.15,
            "engagement": 0.15,
            "semantic": 0.1
        }

    def rank(self, results: list[dict], bm25_scores: list[float], semantic_scores: list[float]) -> list[tuple[dict, float]]:
        scored_results = []
        
        max_bm25 = max(bm25_scores) if bm25_scores else 100
        max_semantic = max(semantic_scores) if semantic_scores else 100
        
        for i, result in enumerate(results):
            bm25_score = bm25_scores[i] if i < len(bm25_scores) else 0
            semantic_score = semantic_scores[i] if i < len(semantic_scores) else 0
            
            bm25_normalized = self._normalize(bm25_score, 0, max_bm25)
            semantic_normalized = self._normalize(semantic_score, 0, max_semantic)
            
            authority_score = self._calculate_authority(result)
            recency_score = self._calculate_recency(result)
            engagement_score = self._calculate_engagement(result)
            
            final_score = (
                self.weights["relevance"] * bm25_normalized +
                self.weights["semantic"] * semantic_normalized +
                self.weights["authority"] * authority_score +
                self.weights["recency"] * recency_score +
                self.weights["engagement"] * engagement_score
            )
            scored_results.append((result, final_score))
        
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results

    def _normalize(self, score: float, min_val: float = 0, max_val: float = 100) -> float:
        if max_val == min_val:
            return 0.5
        normalized = (score - min_val) / (max_val - min_val)
        return max(0, min(1, normalized))

    def _calculate_authority(self, result: dict) -> float:
        followers = result.get("author_followers", 0)
        
        if followers > 10000:
            return 1.0
        elif followers > 5000:
            return 0.8
        elif followers > 1000:
            return 0.6
        elif followers > 100:
            return 0.4
        else:
            return 0.2

    def _calculate_recency(self, result: dict) -> float:
        published_at = result.get("published_at")
        
        if isinstance(published_at, str):
            try:
                published_at = datetime.fromisoformat(published_at)
            except:
                return 0.5
        
        days_old = (datetime.now(published_at.tzinfo) - published_at).days
        
        if days_old <= 7:
            return 1.0
        elif days_old <= 30:
            return 0.8
        elif days_old <= 90:
            return 0.6
        elif days_old <= 180:
            return 0.4
        else:
            return 0.2

    def _calculate_engagement(self, result: dict) -> float:
        views = result.get("views", 0)
        likes = result.get("likes", 0)
        comments = result.get("comments", 0)
        engagement_score = (views * 0.5 + likes * 2 + comments * 3) / 100
        
        return min(1.0, engagement_score)

    def boost_trending(self, results: list[tuple[dict, float]], trending_topics: list[str]) -> list[tuple[dict, float]]:
        boosted = []
        
        for result, score in results:
            boost = 1.0
            
            result_tags = set(result.get("tags", []))
            trending_set = set(trending_topics)
            
            if result_tags & trending_set:
                boost = 1.2
            boosted.append((result, score * boost))
        
        boosted.sort(key=lambda x: x[1], reverse=True)
        return boosted