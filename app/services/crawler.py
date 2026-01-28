import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# --- CONFIGURATION: DEFINE YOUR WEBSITES HERE ---
TARGETS = [
    {
        "name": "DVWA (XAMPP)",
        "base_url": "http://127.0.0.1/DVWA/",
        "waf_url": "http://127.0.0.1:8080", # The WAF port
        "login_type": "dvwa_form",          # Strategy to use
        "creds": {"user": "admin", "pass": "password"}
    },
    {
        "name": "Test Site (Public)",
        "base_url": "http://127.0.0.1/test/",
        "waf_url": "http://127.0.0.1:8080",
        "login_type": "none",               # No login needed
        "creds": {}
    }
    # Add Juice Shop or others here...
]

class MultiCrawler:
    def __init__(self):
        self.session = requests.Session()
        # Common settings for all sites
        self.session.cookies.set("security", "low") 
        self.visited = set()
        self.queue = []

    def to_waf_url(self, target_cfg, path):
        """Converts real URL to WAF URL based on the current target config"""
        # Ensure path is absolute
        if not path.startswith("http"):
             # If it's a relative path like "login.php", join it to base
             full_real_url = urljoin(target_cfg["base_url"], path)
        else:
             full_real_url = path

        parsed = urlparse(full_real_url)
        # Reconstruct: WAF_BASE + PATH
        return f"{target_cfg['waf_url']}{parsed.path}?{parsed.query}"

    # --- STRATEGY: DVWA LOGIN ---
    def login_dvwa(self, target_cfg):
        """Specific login logic for DVWA"""
        login_url = urljoin(target_cfg["base_url"], "login.php")
        waf_login_url = self.to_waf_url(target_cfg, login_url)
        
        print(f"[*] [{target_cfg['name']}] Fetching Token from {waf_login_url}...")
        try:
            r = self.session.get(waf_login_url)
            soup = BeautifulSoup(r.text, "html.parser")
            token_input = soup.find("input", {"name": "user_token"})
            
            if not token_input:
                print("[-] Token not found.")
                return False

            token = token_input["value"]
            payload = {
                "username": target_cfg["creds"]["user"],
                "password": target_cfg["creds"]["pass"],
                "Login": "Login",
                "user_token": token
            }
            headers = {"Referer": waf_login_url}

            # POST login
            r = self.session.post(waf_login_url, data=payload, headers=headers)
            if "Welcome" in r.text or "logout" in r.text:
                print("[+] Login SUCCESS!")
                return True
        except Exception as e:
            print(f"[-] Login Error: {e}")
        return False

    # --- MAIN CRAWL LOGIC ---
   # --- MAIN CRAWL LOGIC ---
    def run(self):
        for target in TARGETS:
            print(f"\n--- STARTING CRAWL: {target['name']} ---")
            self.visited.clear()
            self.queue.clear()
            self.session.cookies.clear() 
            self.session.cookies.set("security", "low")

            # 1. Handle Authentication
            if target["login_type"] == "dvwa_form":
                if not self.login_dvwa(target):
                    print("[-] Skipping this site due to login failure.")
                    continue
            elif target["login_type"] == "none":
                print("[*] No login required. Proceeding.")

            # 2. Seed the Queue
            start_url = self.to_waf_url(target, target["base_url"])
            self.queue.append(start_url)

            # 3. Crawl Loop
            while self.queue:
                url = self.queue.pop(0)
                if url in self.visited: continue
                
                if any(x in url for x in ["logout", "setup", "reset"]): continue

                try:
                    print(f"   Crawling: {url}")
                    r = self.session.get(url)
                    self.visited.add(url)

                    soup = BeautifulSoup(r.text, "html.parser")
                    for link in soup.find_all("a", href=True):
                        href = link["href"]
                        if href.startswith("#") or href.startswith("javascript"): continue
                        
                        # Convert relative link to absolute
                        full_url = urljoin(url, href)
                        
                        # -----------------------------------------------------------
                        # THE FIX: STRICT SCOPE CHECKING
                        # -----------------------------------------------------------
                        # 1. Get the "Real" Target URL (e.g. http://127.0.0.1/DVWA/)
                        target_base = target["base_url"]
                        
                        # 2. Get the "WAF" Target URL (e.g. http://127.0.0.1:8080/DVWA/)
                        waf_target_base = self.to_waf_url(target, target_base).split("?")[0]

                        # 3. Check: Does the link start with EITHER of these?
                        # This prevents "github.com/DVWA" because it doesn't start with 127.0.0.1
                        in_scope = full_url.startswith(target_base) or full_url.startswith(waf_target_base)
                        
                        if in_scope and full_url not in self.visited and full_url not in self.queue:
                             self.queue.append(full_url)
                        # -----------------------------------------------------------
                    
                    time.sleep(0.1)

                except Exception as e:
                    print(f"   Error: {e}")

if __name__ == "__main__":
    bot = MultiCrawler()
    bot.run()