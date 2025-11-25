# ==================== ENHANCED STOCK AGENT ====================
import time
import requests
from typing import Dict
from config import Config

class StockAgent:
    def __init__(self, web_search_agent):
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

