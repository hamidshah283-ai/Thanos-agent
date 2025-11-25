# ==================== FIXED MASTER ORCHESTRATOR ====================
import json
from typing import Dict, List
from openai import OpenAI
from config import Config
from agents import WebSearchAgent, StockAgent, NewsAgent, ResearchAgent

class MasterOrchestrator:
    def __init__(self):
        self.web_search_agent = WebSearchAgent()
        self.stock_agent = StockAgent(self.web_search_agent)
        self.news_agent = NewsAgent(self.web_search_agent)
        self.research_agent = ResearchAgent(self.web_search_agent)
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
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
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
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
                    # Note: This method doesn't exist in ResearchAgent, but keeping for compatibility
                    research_results[symbol] = {"error": "Company profile research not implemented"}
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
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
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
                if 'articles' in news_data:
                    articles = news_data['articles']
                    for article in articles[:2]:
                        response_parts.append(f"  • {article.get('title', 'No title')}")
        
        response_parts.append("\n🔧 Agents used: Web Search + relevant API agents")
        return "\n".join(response_parts)

