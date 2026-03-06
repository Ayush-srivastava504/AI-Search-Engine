import re
from app.config import settings


class SnippetGenerator:
    def __init__(self, max_length: int = settings.max_snippet_length):
        self.max_length = max_length

    def generate(self, content: str, query: str, context_words: int = 10) -> str:
        if not content or not query:
            return content[:self.max_length]

        query_terms = query.lower().split()
        content_lower = content.lower()

        best_match_pos = None
        for term in query_terms:
            if len(term) > 2:
                pos = content_lower.find(term)
                if pos != -1:
                    best_match_pos = pos
                    break

        if best_match_pos is None:
            return content[:self.max_length] + "..."

        start = max(0, best_match_pos - (context_words * 5))
        end = min(len(content), best_match_pos + (context_words * 10))

        snippet = content[start:end].strip()
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        if len(snippet) > self.max_length:
            snippet = snippet[:self.max_length] + "..."

        return snippet

    def highlight_terms(self, text: str, terms: list[str]) -> str:
        for term in terms:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            text = pattern.sub(f"<mark>{term}</mark>", text)
        
        return text

    def extract_sentences_with_query(self, content: str, query: str, num_sentences: int = 2) -> str:
        sentences = re.split(r'[.!?]+', content)
        query_terms = set(query.lower().split())
        
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = sum(1 for term in query_terms if term.lower() in sentence.lower())
            if score > 0:
                scored_sentences.append((score, i, sentence.strip()))

        if not scored_sentences:
            return content[:self.max_length]

        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        
        top_sentences = sorted(scored_sentences[:num_sentences], key=lambda x: x[1])
        snippet = " ".join([s[2] for s in top_sentences])

        if len(snippet) > self.max_length:
            snippet = snippet[:self.max_length] + "..."

        return snippet