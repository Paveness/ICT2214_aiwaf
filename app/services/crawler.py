import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# CONFIGURATION
# ---------------------------------------------------------
# Your WAF Address (Must match run.py port)
WAF_PROXY = "http://127.0.0.1:8080"  

# Where DVWA actually lives (XAMPP usually Port 80)
# Note: We point to 127.0.0.1 to avoid cookie mismatch issues
TARGET_BASE = "http://127.0.0.1/DVWA/" 
LOGIN_URL = urljoin(TARGET_BASE, "login.php")

# DVWA Credentials
USERNAME = "admin"
PASSWORD = "password"

class AuthenticatedCrawler:
    def __init__(self):
        # 1. Create a Session
        self.session = requests.Session()
        
        # 2. FORCE SECURITY LEVEL TO LOW
        # This is critical for DVWA automation
        self.session.cookies.set("security", "low") 
        
        self.visited = set()
        self.queue = [] 

    def get_csrf_token(self):
        """Fetches the login page to get the hidden user_token"""
        target = self.to_waf_url(LOGIN_URL)
        print(f"[*] Fetching CSRF token from {target}...")
        
        try:
            r = self.session.get(target)
            soup = BeautifulSoup(r.text, "html.parser")
            
            token = soup.find("input", {"name": "user_token"})
            if token:
                return token["value"]
        except Exception as e:
            print(f"[-] Error fetching token: {e}")
            
        return None

    def login(self):
        """Performs the login dance with redirect fixes"""
        token = self.get_csrf_token()
        if not token:
            print("[-] Could not find CSRF token. Is XAMPP running?")
            return False

        print(f"[*] Found Token: {token}. Attempting Login...")
        
        payload = {
            "username": USERNAME,
            "password": PASSWORD,
            "Login": "Login",
            "user_token": token
        }

        # Add Referer for strict security checks
        headers = {
            "Referer": self.to_waf_url(LOGIN_URL),
            "User-Agent": "NeuroWAF-Crawler"
        }

        # Send Login POST
        target = self.to_waf_url(LOGIN_URL)
        
        # Disable automatic redirects to handle them manually
        try:
            r = self.session.post(target, data=payload, headers=headers, allow_redirects=False)
            
            # Manually handle the redirect
            if r.status_code in [302, 301] and "Location" in r.headers:
                raw_location = r.headers["Location"]
                
                # Fix relative redirects (e.g. "index.php" -> "http://.../index.php")
                next_url = urljoin(target, raw_location)
                
                # Force back to WAF Port 8080 if it escaped to Port 80
                if "127.0.0.1/DVWA" in next_url and "8080" not in next_url:
                    next_url = next_url.replace("127.0.0.1/DVWA", "127.0.0.1:8080/DVWA")
                elif "localhost/DVWA" in next_url and "8080" not in next_url:
                    next_url = next_url.replace("localhost/DVWA", "127.0.0.1:8080/DVWA")

                print(f"[DEBUG] Following redirect to: {next_url}")
                r = self.session.get(next_url)

            # Check success
            if "Welcome to Damn Vulnerable Web App" in r.text or "logout.php" in r.text:
                print("[+] Login SUCCESS!")
                return True
            else:
                print("[-] Login FAILED. Check credentials or Database.")
                return False
                
        except Exception as e:
            print(f"[-] Login Exception: {e}")
            return False

    def to_waf_url(self, original_url):
        """Converts http://127.0.0.1/DVWA/x -> http://127.0.0.1:8080/DVWA/x"""
        parsed = urlparse(original_url)
        # Rebuild pointing to WAF port 8080
        # We manually construct it to be safe
        path = parsed.path
        if not path.startswith("/"):
             path = "/" + path
        
        return f"{WAF_PROXY}{path}?{parsed.query}"

    def crawl(self):
        """The Main Loop"""
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
            
            # Skip dangerous pages
            if any(x in url for x in ["logout.php", "setup.php", "security.php"]):
                print(f"   [SKIP] Dangerous URL: {url}")
                continue

            try:
                print(f"   Crawling: {url}")
                r = self.session.get(url)
                self.visited.add(url)
                
                soup = BeautifulSoup(r.text, "html.parser")
                found_links = soup.find_all("a", href=True)

                for link in found_links:
                    href = link["href"]
                    
                    if href.startswith("javascript") or href.startswith("#"):
                        continue

                    full_url = urljoin(url, href)
                    
                    # Logic: Must be DVWA, Must be Local, Must not be visited
                    is_dvwa = "DVWA" in full_url
                    is_local = "127.0.0.1" in full_url or "localhost" in full_url
                    not_visited = full_url not in self.visited and full_url not in self.queue

                    if is_dvwa and is_local and not_visited:
                        self.queue.append(full_url)

                time.sleep(0.2) 

            except Exception as e:
                print(f"   Error crawling {url}: {e}")

if __name__ == "__main__":
    bot = AuthenticatedCrawler()
    bot.crawl()