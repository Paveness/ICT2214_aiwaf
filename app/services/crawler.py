import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re

# CONFIGURATION
# ---------------------------------------------------------
WAF_PROXY = "http://localhost:8080"  # Your WAF address
TARGET_BASE = "http://localhost/DVWA/" # Where DVWA lives (XAMPP usually port 80)
LOGIN_URL = urljoin(TARGET_BASE, "login.php")

# DVWA Credentials
USERNAME = "admin"
PASSWORD = "password"

class AuthenticatedCrawler:
    def __init__(self):
        # 1. Create a Session to hold cookies (Login state)
        self.session = requests.Session()
        
        # 2. Configure Session to go through WAF Proxy? 
        # Actually, for the WAF to learn, we send requests TO the WAF.
        # But since WAF forwards to 80, we just need to hit localhost:8080.
        # We will dynamically replace the URL base.
        self.visited = set()
        self.queue = [] 

    def get_csrf_token(self):
        """Fetches the login page to get the hidden user_token"""
        # We hit the target directly for the token to ensure we get it right first
        # Or hit it through WAF. Let's try through WAF.
        target = self.to_waf_url(LOGIN_URL)
        print(f"[*] Fetching CSRF token from {target}...")
        
        r = self.session.get(target)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # DVWA hidden token field name is 'user_token'
        token = soup.find("input", {"name": "user_token"})
        if token:
            return token["value"]
        return None

    def login(self):
        """Performs the login dance"""
        token = self.get_csrf_token()
        if not token:
            print("[-] Could not find CSRF token. Is DVWA running?")
            return False

        print(f"[*] Found Token: {token}. Attempting Login...")
        
        payload = {
            "username": USERNAME,
            "password": PASSWORD,
            "Login": "Login", # Submit button name is required by DVWA
            "user_token": token
        }

        # Send Login POST
        target = self.to_waf_url(LOGIN_URL)
        r = self.session.post(target, data=payload)
        
        if "Welcome to Damn Vulnerable Web App" in r.text or "logout.php" in r.text:
            print("[+] Login SUCCESS!")
            return True
        else:
            print("[-] Login FAILED. Check credentials.")
            return False

    def to_waf_url(self, original_url):
        """Converts http://localhost/DVWA/x -> http://localhost:8080/DVWA/x"""
        # Parse the original path
        parsed = urlparse(original_url)
        # Rebuild pointing to WAF port 8080
        return f"{WAF_PROXY}{parsed.path}?{parsed.query}"

    def crawl(self):
        if not self.login():
            return

        # Start crawling at the index
        start_node = self.to_waf_url(TARGET_BASE)
        self.queue.append(start_node)
        
        print(f"[*] Starting Authenticated Crawl...")

        while self.queue:
            url = self.queue.pop(0)
            
            if url in self.visited:
                continue
            
            # Avoid logging out!
            if "logout.php" in url or "setup.php" in url:
                continue

            try:
                # REQUEST
                print(f"   Crawling: {url}")
                r = self.session.get(url)
                self.visited.add(url)
                
                # PARSE
                soup = BeautifulSoup(r.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    
                    # Handle relative links
                    full_url = urljoin(url, href)
                    
                    # Convert to WAF URL structure for the queue
                    if "DVWA" in full_url and full_url not in self.visited:
                        # Ensure we don't jump out of WAF scope
                        if "localhost" in full_url:
                            self.queue.append(full_url)
                
                time.sleep(0.2) # Be nice

            except Exception as e:
                print(f"   Error: {e}")

if __name__ == "__main__":
    bot = AuthenticatedCrawler()
    bot.crawl()