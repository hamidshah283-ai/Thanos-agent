# 🚀 THANOS-LEVEL AI STOCK AGENT - FIXED VERSION

import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI
from googlesearch import search
import time
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class Config:
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
    ZENROWS_KEY = os.getenv('ZENROWS_KEY')

# ==================== WEB SEARCH AGENT ====================
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

# ==================== ENHANCED STOCK AGENT ====================
class StockAgent:
    def __init__(self, web_search_agent: WebSearchAgent):
        self.api_key = Config.ALPHA_VANTAGE_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.web_search = web_search_agent
    
    def get_current_price(self, symbol: str) -> Dict:
        """Get real-time stock price with web-enhanced context"""
        # API data
        api_data = self._get_api_price(symbol)
        
        # Web search for additional context
        web_context = self.web_search.search_web(
            f"{symbol} stock price today market analysis", 
            num_results=2
        )
        
        return {
            'api_data': api_data,
            'web_context': web_context,
            'timestamp': time.time()
        }
    
    def _get_api_price(self, symbol: str) -> Dict:
        """Get stock price from Alpha Vantage"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': symbol,
                    'price': quote.get('05. price', 'N/A'),
                    'change': quote.get('09. change', 'N/A'),
                    'change_percent': quote.get('10. change percent', 'N/A'),
                    'high': quote.get('03. high', 'N/A'),
                    'low': quote.get('04. low', 'N/A'),
                    'volume': quote.get('06. volume', 'N/A')
                }
            else:
                return {'error': f"Could not fetch data for {symbol}"}
                
        except Exception as e:
            return {'error': f"Stock API error: {str(e)}"}

# ==================== ENHANCED NEWS AGENT ====================
class NewsAgent:
    def __init__(self, web_search_agent: WebSearchAgent):
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

# ==================== ENHANCED RESEARCH AGENT ====================
class ResearchAgent:
    def __init__(self, web_search_agent: WebSearchAgent):
        self.api_key = Config.ZENROWS_KEY
        self.base_url = "https://api.zenrows.com/v1/"
        self.web_search = web_search_agent
    
    def research_product_prices(self, product: str, country: str = "Pakistan") -> Dict:
        """Research product prices with actual web scraping"""
        # For known retailers, use direct URLs
        known_urls = {
            'skygames': 'https://www.skygames.com.pk/product/ps5-pro-playstation-5-pro-2tb/',
            'gamepark': 'https://gamepark.pk/product/ps5-pro-2tb-playstation-5-pro/',
            'gameforce': 'https://gameforce.pk/product/ps5-pro-digital-edition-2tb-console-playstation-5-pro-price-in-pakistan/'
        }
        
        scraped_prices = {}
        for store, url in known_urls.items():
            price = self.scrape_prices(url)
            scraped_prices[store] = {
                'url': url,
                'scraped_price': price
            }
        
        return {
            'scraped_prices': scraped_prices,
            'product': product
        }
    
    def scrape_prices(self, url: str) -> str:
        """Extract actual prices from product pages USING ZenRows"""
        try:
            # USE ZenRows API instead of direct requests
            zenrows_params = {
                'url': url,
                'apikey': self.api_key,
                'premium_proxy': 'true',
                'antibot': 'true'
            }
            
            print(f"🔍 Scraping with ZenRows: {url}")
            response = requests.get(self.base_url, params=zenrows_params, timeout=15)
            print(f"📊 ZenRows response status: {response.status_code}")
            
            # Save HTML for debugging
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("💾 Saved page HTML to debug_page.html for inspection")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # More specific price selectors for Pakistani e-commerce
            price_selectors = [
                '.price', '.woocommerce-Price-amount', '.product-price',
                '.price-box', '.special-price', '.current-price',
                '[class*="price"]', '[class*="Price"]', '.amount',
                '.product__price', '.p-price', '.selling-price',
                '.woocommerce-Price-amount.amount', '.summary .price',
                '.product-details .price', '.product-info .price'
            ]
            
            all_prices = []
            
            for selector in price_selectors:
                price_elements = soup.select(selector)
                if price_elements:
                    print(f"✅ Found {len(price_elements)} elements with selector: {selector}")
                
                for element in price_elements:
                    text = element.get_text().strip()
                    # Clean up the text
                    text = ' '.join(text.split())  # Remove extra whitespace
                    
                    # Look for Pakistani rupee patterns
                    if any(word in text.lower() for word in ['pkr', 'rs', '₨', 'rupees', 'rp', '/-']):
                        all_prices.append(f"{selector}: '{text}'")
                        print(f"💰 Pakistani price candidate: {text}")
                    elif any(char.isdigit() for char in text) and len(text) > 3:
                        # If it has numbers and looks substantial, consider it
                        # Check if it looks like a price (has digits and common price symbols)
                        if any(symbol in text for symbol in [',', '.', '$', '€', '£', '₹']) or len(text) <= 20:
                            all_prices.append(f"{selector}: '{text}'")
                            print(f"💰 Price candidate: {text}")
            
            # Also try to find prices in meta tags
            meta_price_selectors = [
                'meta[property="og:price:amount"]',
                'meta[itemprop="price"]',
                'meta[name="price"]'
            ]
            
            for meta_selector in meta_price_selectors:
                meta_elements = soup.select(meta_selector)
                for meta in meta_elements:
                    content = meta.get('content', '').strip()
                    if content and any(char.isdigit() for char in content):
                        all_prices.append(f"Meta {meta_selector}: '{content}'")
                        print(f"💰 Meta price: {content}")
            
            if all_prices:
                print(f"💰 All price candidates found: {all_prices}")
                # Return the most likely price (usually the first one or one with PKR)
                for price in all_prices:
                    if any(currency in price.lower() for currency in ['pkr', 'rs']):
                        return f"Primary Price: {price}"
                return f"Multiple prices found: {', '.join(all_prices[:3])}"
            
            # If no prices found with selectors, try to find any text that looks like prices
            print("🔍 No prices found with selectors, searching entire page...")
            all_text = soup.get_text()
            lines = all_text.split('\n')
            price_lines = []
            
            for line in lines:
                line = line.strip()
                if len(line) < 100:  # Reasonable length for a price
                    # Look for lines with numbers and currency indicators
                    if (any(char.isdigit() for char in line) and 
                        any(indicator in line.lower() for indicator in ['pkr', 'rs', 'price', 'cost', '₨', 'rupee'])):
                        price_lines.append(line)
                        print(f"💰 Text price candidate: {line}")
            
            if price_lines:
                return f"Text prices found: {', '.join(price_lines[:5])}"
            
            return "No clear price found on page"
            
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            return f"Could not access page: {str(e)}"
            
# ==================== FIXED MASTER ORCHESTRATOR ====================
class MasterOrchestrator:
    def __init__(self):
        self.web_search_agent = WebSearchAgent()
        self.stock_agent = StockAgent(self.web_search_agent)
        self.news_agent = NewsAgent(self.web_search_agent)
        self.research_agent = ResearchAgent(self.web_search_agent)
    
    def analyze_intent(self, user_input: str) -> Dict:
        """Use GPT-4 to analyze user intent"""
        
        prompt = f"""
        Analyze this user query and determine what information services are needed.
        User Query: "{user_input}"

        If the query asks for PRODUCT PRICES, set "primary_intent" to "research" and "is_financial_query" to false
        
        Respond in JSON format:
        {{
            "primary_intent": "stock_price|news|research|general_news|combined",
            "symbols": ["AAPL", "TSLA"] or [],
            "needs_stock": true/false,
            "needs_news": true/false, 
            "needs_research": true/false,
            "needs_web_search": true/false,
            "is_financial_query": true/false,
            "search_queries": ["search query based on user input"]
        }}
        
        IMPORTANT: If the query is about general news, politics, or non-financial topics, set "is_financial_query" to false and "symbols" to empty array.
        """
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            intent_data = json.loads(response.choices[0].message.content)
            
            # Ensure symbols is always a list
            if 'symbols' not in intent_data:
                intent_data['symbols'] = []
                
            return intent_data
            
        except Exception as e:
            print(f"⚠️ Intent analysis failed: {e}")
            # Smart fallback
            input_lower = user_input.lower()
            is_financial = any(word in input_lower for word in ['stock', 'price', 'market', 'investment', 'earnings', 'company'])
            
            return {
                "primary_intent": "general_news" if not is_financial else "news",
                "symbols": self._extract_symbols(user_input) if is_financial else [],
                "needs_stock": is_financial,
                "needs_news": True,
                "needs_research": is_financial,
                "needs_web_search": True,
                "is_financial_query": is_financial,
                "search_queries": [user_input]
            }
    
    def _extract_symbols(self, text: str) -> List[str]:
        """Extract potential stock symbols from text"""
        words = text.upper().split()
        symbols = [word for word in words if len(word) <= 5 and word.isalpha()]
        return symbols[:2]
    
    def execute_agents(self, intent_analysis: Dict) -> Dict:
        """Execute the appropriate agents based on intent analysis"""
        results = {}
        
        symbols = intent_analysis.get('symbols', [])
        is_financial = intent_analysis.get('is_financial_query', True)
        
        # Web search for general context
        if intent_analysis.get('needs_web_search', False):
            search_queries = intent_analysis.get('search_queries', ["general query"])
            web_context = {}
            for query in search_queries[:2]:
                web_context[query] = self.web_search_agent.search_web(query, num_results=3)
            results['web_search'] = web_context
        
        # News Agent (handles both financial and general news)
        if intent_analysis.get('needs_news', False):
            if symbols and is_financial:
                # Financial news for specific symbols
                news_results = {}
                for symbol in symbols:
                    news_results[symbol] = self.news_agent.get_news(symbol, is_financial=True)
                results['news'] = news_results
            else:
                # General news - use the search queries or user input
                search_query = intent_analysis.get('search_queries', ["general query"])[0]
                results['news'] = {'general': self.news_agent.get_news(search_query, is_financial=False)}
        
        # Only run financial agents for financial queries
        if is_financial and symbols:
            # Stock Price Agent
            if intent_analysis.get('needs_stock', False):
                stock_results = {}
                for symbol in symbols:
                    print(f"📈 Fetching stock data for {symbol}...")
                    stock_results[symbol] = self.stock_agent.get_current_price(symbol)
                results['stock_data'] = stock_results
        
        # Research Agent - should work for BOTH financial and non-financial queries
        if intent_analysis.get('needs_research', False):
            if not intent_analysis.get('is_financial_query', True):
                # PRODUCT RESEARCH - This should run for PS5 queries
                search_query = intent_analysis.get('search_queries', ["product inquiry"])[0]
                print(f"🔍 Research Agent searching for: {search_query}")
                results['product_research'] = self.research_agent.research_product_prices(search_query)
            elif symbols and is_financial:  # Financial research
                research_results = {}
                for symbol in symbols:
                    research_results[symbol] = self.research_agent.get_company_profile(symbol)
                results['research'] = research_results
        
        return results

    def synthesize_response(self, user_input: str, agent_results: Dict, intent_analysis: Dict) -> str:
        """Use OpenAI to synthesize all agent results into a coherent response"""
        
        clean_results = self._clean_results(agent_results)
        results_str = json.dumps(clean_results, indent=2)
        
        prompt = f"""
        You are a comprehensive information assistant with access to:
        - Real-time stock data APIs
        - Financial news APIs  
        - Company research databases
        - Live web search results
        
        The user asked: "{user_input}"
        
        Here are the combined results from ALL sources (APIs + Web Search):
        {results_str}
        
        Please provide a comprehensive, well-structured response that:
        1. Directly answers the user's question using ALL available data
        2. Highlights key insights from both API data and web sources
        3. Provides context and analysis
        4. Includes recent developments found through web search
        
        At the end, mention which agents were used (Stock Agent, News Agent, Research Agent, Web Search).
        
        Format: Professional but conversational, with clear sections.
        """
        
        try:
            print("🤖 Generating response with OpenAI...")
            response = openai_client.chat.completions.create(
                model="gpt-4",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return self._create_fallback_response(user_input, clean_results)
    
    def _clean_results(self, agent_results: Dict) -> Dict:
        """Clean results to ensure they're JSON serializable"""
        try:
            return json.loads(json.dumps(agent_results, default=str))
        except:
            clean = {}
            for key, value in agent_results.items():
                if isinstance(value, (str, int, float, bool, type(None))):
                    clean[key] = value
                else:
                    clean[key] = str(value)
            return clean
    
    def _create_fallback_response(self, user_input: str, results: Dict) -> str:
        """Create a fallback response when API fails"""
        response_parts = [f"Regarding '{user_input}':\n"]
        
        if 'stock_data' in results:
            response_parts.append("📈 STOCK DATA:")
            for symbol, data in results['stock_data'].items():
                if 'api_data' in data and 'price' in data['api_data']:
                    price_data = data['api_data']
                    response_parts.append(
                        f"  {symbol}: ${price_data.get('price', 'N/A')} "
                        f"({price_data.get('change_percent', 'N/A')})"
                    )
        
        if 'news' in results:
            response_parts.append("\n📰 LATEST NEWS:")
            for key, news_data in results['news'].items():
                if 'api_news' in news_data and 'articles' in news_data['api_news']:
                    articles = news_data['api_news']['articles']
                    for article in articles[:2]:
                        response_parts.append(f"  • {article.get('title', 'No title')}")
        
        response_parts.append("\n🔧 Agents used: Web Search + relevant API agents")
        return "\n".join(response_parts)

# ==================== ENHANCED CHATBOT INTERFACE ====================
class FinancialChatbot:
    def __init__(self):
        self.orchestrator = MasterOrchestrator()
    
    def process_query(self, user_input: str) -> str:
        """Main method to process user queries"""
        print(f"🔍 Analyzing: {user_input}")
        
        try:
            # Step 1: Analyze intent
            intent_analysis = self.orchestrator.analyze_intent(user_input)
            print(f"🎯 Intent: {intent_analysis['primary_intent']}")
            print(f"💼 Financial: {intent_analysis.get('is_financial_query', False)}")
            print(f"🌐 Web Search: {intent_analysis.get('needs_web_search', False)}")
            
            # Step 2: Execute appropriate agents
            agent_results = self.orchestrator.execute_agents(intent_analysis)
            print(f"📊 Agent results collected")
            
            # Step 3: Synthesize final response
            final_response = self.orchestrator.synthesize_response(user_input, agent_results, intent_analysis)
            
            return final_response
            
        except Exception as e:
            error_msg = f"❌ System error: {str(e)}"
            print(error_msg)
            return f"I encountered a system error. Please try again with a simpler query."

# ==================== MAIN EXECUTION ====================
def main():
    print("🚀 THANOS-LEVEL AI AGENT ACTIVATED!")
    print("💎 You have all the infinity stones (APIs + Web Search)")
    print("Type 'quit' to exit\n")
    
    chatbot = FinancialChatbot()
    
    while True:
        user_input = input("\n💬 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            response = chatbot.process_query(user_input)
            print(f"\n🤖 Analyst: {response}")
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()