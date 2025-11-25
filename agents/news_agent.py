# ==================== ENHANCED NEWS AGENT ====================
from typing import Dict

class NewsAgent:
    def __init__(self, web_search_agent):
        self.web_search = web_search_agent
    
    def get_news(self, query: str, is_financial: bool = True) -> Dict:
        """Get news using comprehensive web search only"""
        
        # Create better search queries based on topic
        if is_financial:
            search_queries = [
                f"{query} financial news",
                f"{query} market news",
                f"{query} business updates"
            ]
        else:
            search_queries = [
                f"{query} latest news",
                f"{query} breaking news", 
                f"{query} recent developments",
                f"{query} updates 2025"
            ]
        
        # Search multiple queries for comprehensive coverage
        all_articles = []
        sources_used = set()
        
        for search_query in search_queries[:2]:  # Use first 2 queries
            print(f"📰 News searching: {search_query}")
            web_results = self.web_search.search_web(search_query, num_results=5)
            
            for result in web_results.get('search_results', []):
                # Filter out duplicates and low-quality results
                title = result.get('title', '').lower()
                url = result.get('url', '')
                
                # Skip if already seen or low quality
                if (url not in sources_used and 
                    len(title) > 10 and 
                    not any(spam in title for spam in ['advertisement', 'sponsored', 'click here'])):
                    
                    all_articles.append({
                        'title': result.get('title', ''),
                        'source': self._extract_source(url),
                        'url': url,
                        'description': result.get('description', ''),
                        'search_query': search_query
                    })
                    sources_used.add(url)
        
        return {
            'articles': all_articles[:8],  # Return top 8 unique articles
            'total_results': len(all_articles),
            'query_used': query,
            'is_financial': is_financial,
            'sources': list(sources_used)[:5]
        }
    
    def _extract_source(self, url: str) -> str:
        """Extract clean source name from URL"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Clean up domain name
            if 'www.' in domain:
                domain = domain.replace('www.', '')
            return domain.split('.')[0].title()
        except:
            return "Unknown Source"

