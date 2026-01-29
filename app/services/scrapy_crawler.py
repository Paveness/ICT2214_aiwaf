import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import FormRequest
from urllib.parse import urljoin, urlparse

# CONFIGURATION
# --------------------------------------------------
WAF_BASE = 'http://127.0.0.1:8080' 

class NeuroSpider(scrapy.Spider):
    name = 'neuro_waf_spider'
    allowed_domains = ['127.0.0.1', 'localhost']

    def start_requests(self):
        print("🕷️ Starting Scrapy Spider...")
        # Start at login
        start_url = f"{WAF_BASE}/DVWA/login.php"
        yield scrapy.Request(
            url=start_url, 
            callback=self.parse_login_page,
            cookies={'security': 'low'},
            meta={'dont_merge_cookies': False} 
        )

    def parse_login_page(self, response):
        print(f"[*] Fetching Token from {response.url}")
        token = response.css("input[name='user_token']::attr(value)").get()
        
        if not token:
            print("[-] No Token found! (Is DVWA running?)")
            return

        print(f"[*] Found Token: {token}. Attempting Login...")
        
        return FormRequest.from_response(
            response,
            formdata={
                'username': 'admin', 
                'password': 'password', 
                'Login': 'Login', 
                'user_token': token
            },
            headers={
                'Referer': response.url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' 
            },
            cookies={'security': 'low'}, 
            callback=self.after_login,
            dont_filter=True 
        )

    def after_login(self, response):
        if "login.php" in response.url:
             print("❌ Login FAILED. Database reset likely needed.")
             return

        if "Welcome to Damn Vulnerable Web App" in response.text:
            print("✅ Login Success! Starting Crawl...")
            yield scrapy.Request(
                url=f"{WAF_BASE}/DVWA/", 
                callback=self.parse,
                cookies={'security': 'low'}
            )
        else:
            print(f"⚠️ Unknown State. Landed on {response.url}")

    def parse(self, response):
        # 1. SAFETY CHECK: Ignore PDFs, Images, Zips, etc.
        content_type = response.headers.get(b'Content-Type', b'').decode('utf-8').lower()
        if 'text/html' not in content_type:
            print(f"⏩ Skipping non-HTML file: {response.url} ({content_type})")
            return

        # 2. LOGGING CURRENT URL
        print(f"🔍 Crawling: {response.url}")

        # 3. Scan page for links
        for href in response.css('a::attr(href)').getall():
            if href.startswith("http"):
                full_url = href
            else:
                full_url = response.urljoin(href)

            # Filter: Only follow links inside DVWA
            if "DVWA" not in full_url:
                continue

            # Filter: Avoid Logout/Setup
            if any(x in full_url for x in ["logout.php", "setup.php", "security.php"]):
                continue

            # Rewrite Logic: Ensure we stay on WAF port 8080
            if "8080" in full_url:
                yield scrapy.Request(full_url, callback=self.parse, cookies={'security': 'low'})
            elif "127.0.0.1/DVWA" in full_url:
                new_url = full_url.replace("127.0.0.1/DVWA", "127.0.0.1:8080/DVWA")
                yield scrapy.Request(new_url, callback=self.parse, cookies={'security': 'low'})

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'INFO',
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 0.2,
        'COOKIES_ENABLED': True,
    })
    
    process.crawl(NeuroSpider)
    process.start()