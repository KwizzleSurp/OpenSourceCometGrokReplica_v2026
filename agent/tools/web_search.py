"""agent/tools/web_search.py - SearxNG / Tavily wrapper"""
import os, httpx
from typing import List, Dict

def search_web(query: str, n: int = 5) -> List[Dict]:
    url = os.getenv("SEARXNG_URL", "http://localhost:8080")
    key = os.getenv("TAVILY_API_KEY", "")
    try:
        r = httpx.get(f"{url}/search", params={"q": query, "format": "json"}, timeout=10)
        r.raise_for_status()
        res = [{"title": x.get("title"), "url": x.get("url"), "snippet": x.get("content","")}
               for x in r.json().get("results", [])[:n]]
        if res: return res
    except Exception: pass
    if key:
        try:
            r = httpx.post("https://api.tavily.com/search",
                           json={"api_key": key, "query": query, "num_results": n}, timeout=15)
            r.raise_for_status()
            return [{"title": x.get("title"), "url": x.get("url"), "snippet": x.get("content","")}
                    for x in r.json().get("results", [])[:n]]
        except Exception as e: return [{"error": str(e)}]
    return [{"error": "No search backend. Run SearxNG or set TAVILY_API_KEY."}]
