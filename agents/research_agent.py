# ==================== ENHANCED RESEARCH AGENT ====================
import requests
from typing import Dict
from bs4 import BeautifulSoup
from config import Config

class ResearchAgent:
    def __init__(self, web_search_agent):
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

