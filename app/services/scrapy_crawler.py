import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import FormRequest
import random

# CONFIGURATION
# --------------------------------------------------
# WAF Address (This proxies traffic to your Shop on Port 5000)
WAF_BASE = 'http://127.0.0.1:8080' 

class ShopSpider(scrapy.Spider):
    name = 'shop_spider'
    allowed_domains = ['127.0.0.1', 'localhost']
    
    # Start at the Homepage
    start_urls = [f"{WAF_BASE}/"]

    def start_requests(self):
        print("🕷️ Starting NeuroShop Crawler...")
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, cookies={'security': 'low'})

    def parse(self, response):
        print(f"🔍 Crawling: {response.url}")

        # 1. INTERACT WITH FORMS
        # The crawler finds forms and fills them with SAFE data
        for form in response.css('form'):
            action = form.attrib.get('action', '')
            
            # Scenario A: Search Bar (GET Request)
            if "/search" in action or "q" in response.text:
                benign_queries = ["Python", "Hacker", "Security", "AI", "Book"]
                query = random.choice(benign_queries)
                print(f"   [+] Simulating User Search: '{query}'")
                
                # Construct the search URL manually since it's a GET form
                yield scrapy.Request(
                    url=f"{WAF_BASE}/search?q={query}",
                    callback=self.parse
                )

            # Scenario B: Login Form (POST Request)
            elif "/login" in response.url:
                print("   [+] Simulating User Login...")
                yield FormRequest.from_response(
                    response,
                    formdata={
                        'username': 'john',  # Valid user
                        'password': 'securepass'
                    },
                    callback=self.after_login
                )

        # 2. FOLLOW LINKS
        # It clicks on products, categories, nav links, etc.
        for href in response.css('a::attr(href)').getall():
            if href.startswith("/"):
                full_url = f"{WAF_BASE}{href}"
            elif href.startswith("http"):
                full_url = href
            else:
                continue

            # Ensure we stay on the WAF
            if WAF_BASE in full_url:
                yield scrapy.Request(full_url, callback=self.parse)

    def after_login(self, response):
        if "Logout" in response.text or "Welcome" in response.text:
            print("✅ Login Success! Continuing crawl as authenticated user...")
        else:
            print("⚠️ Login finished (Check logs if successful).")
        
        # Continue crawling from the dashboard/home
        yield scrapy.Request(url=f"{WAF_BASE}/", callback=self.parse)

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'INFO',
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 0.5, # Realistic user speed
        'COOKIES_ENABLED': True,
    })
    
    process.crawl(ShopSpider)
    process.start()