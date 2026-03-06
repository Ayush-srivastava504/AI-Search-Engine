import re
from typing import Optional
from datetime import datetime, timedelta


class QueryParser:
    def __init__(self):
        self.operators_pattern = r'(site|author|from|to|tag):(["\']?)([^"\'\s]+)\2'

    def parse(self, query: str) -> dict:
        filters = {
            "site": None,
            "author": None,
            "from_date": None,
            "to_date": None,
            "tags": [],
            "clean_query": query
        }

        matches = re.finditer(self.operators_pattern, query)
        
        for match in matches:
            operator, _, value = match.groups()
            
            if operator == "site":
                filters["site"] = value.lower()
            elif operator == "author":
                filters["author"] = value
            elif operator == "from":
                filters["from_date"] = self._parse_date(value)
            elif operator == "to":
                filters["to_date"] = self._parse_date(value)
            elif operator == "tag":
                filters["tags"].append(value.lower())

        filters["clean_query"] = self._remove_operators(query)
        
        return filters

    def _remove_operators(self, query: str) -> str:
        clean = re.sub(self.operators_pattern, "", query)
        return " ".join(clean.split()).strip()

    def _parse_date(self, date_str: str) -> Optional[str]:
        formats = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.isoformat()
            except ValueError:
                continue

        if date_str.lower() == "today":
            return datetime.now().isoformat()
        elif date_str.lower() == "yesterday":
            return (datetime.now() - timedelta(days=1)).isoformat()
        elif date_str.lower() == "week":
            return (datetime.now() - timedelta(days=7)).isoformat()
        elif date_str.lower() == "month":
            return (datetime.now() - timedelta(days=30)).isoformat()
        
        return None

    def extract_quoted_phrases(self, query: str) -> list[str]:
        pattern = r'"([^"]+)"'
        return re.findall(pattern, query)

    def is_exact_search(self, query: str) -> bool:
        return bool(re.search(r'"[^"]+"', query))