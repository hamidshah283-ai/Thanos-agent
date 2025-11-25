# ==================== WEB SEARCH AGENT ====================
from typing import Dict
from ddgs import DDGS

class WebSearchAgent:
    def __init__(self):
        self.search_cache = {}
        self.ddgs = DDGS()
    
    def search_web(self, query: str, num_results: int = 5) -> Dict:
        """Perform web search using DuckDuckGo"""
        cache_key = f"{query}_{num_results}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]
        
        try:
            print(f"🌐 Searching DuckDuckGo for: {query}")
            search_results = []
            
            # Use DuckDuckGo search
            results = self.ddgs.text(query, max_results=num_results)
            
            for result in results:
                search_results.append({
                    'title': result.get('title', 'No title'),
                    'url': result.get('href', ''),
                    'description': result.get('body', 'No description')[:200] + "..."
                })
            
            result_data = {'search_results': search_results}
            self.search_cache[cache_key] = result_data
            return result_data
            
        except Exception as e:
            print(f"⚠️ DuckDuckGo search error: {e}")
            return {'error': f"Search failed: {str(e)}", 'search_results': []}

