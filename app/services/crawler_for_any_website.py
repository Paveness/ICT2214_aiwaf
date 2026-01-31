import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import time
import re

class AuthenticatedCrawler:
    def __init__(self, origin_url, auth_info=None):
        self.url = self.to_waf_url(origin_url, 8080) # 8080 is waf port
        parsed = urlparse(self.url.strip())
        self.scope = parsed.netloc
        self.auth = auth_info
        
        # create a session
        self.session = requests.Session()
        self.visited = set()
        self.queue = [] 
    
    def to_waf_url(self, original_url: str, waf_port: int = 8080) -> str:
        parsed = urlparse(original_url)

        # Replace only the port
        netloc = parsed.hostname
        if parsed.username and parsed.password:
            netloc = f"{parsed.username}:{parsed.password}@{netloc}"

        netloc = f"{netloc}:{waf_port}"
        return urlunparse((
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        ))

    def in_scope(self, url):
        return urlparse(url).netloc == self.scope

    def login(self):
        if not self.auth :
            print("[*] No authentication configured. Skipping login.")
            return True

        login_url = self.url + self.auth["login_endpoint"]
        login_payload = self.auth["login_payload"]
        # Add Referer for strict security checks
        headers = {
            "Referer": login_url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        # extract token value if have
        if login_payload["token_required"] :
            r = self.session.get(login_url)
            r.raise_for_status()

            soup = BeautifulSoup(r.text, "html.parser")
            token = soup.find("input", {"name": login_payload["token_name"]})
            login_payload[login_payload["token_name"]] = token["value"]
        try:
            next_url = login_url
            r = self.session.post(login_url, data=login_payload, headers=headers, allow_redirects=False)
            location = r.headers.get("Location")
            # next_url = urljoin(self.url, location)
            
           # 1️⃣ Redirect-based success (most reliable)
            if r.status_code in (301, 302, 303, 307, 308) and location:
                next_url = urljoin(login_url, location)

                if (
                    next_url != login_url and
                    login_endpoint not in next_url.lower()
                ):
                    return True

            # 2️⃣ Explicit failure codes
            if r.status_code in (401, 403):
                print("Credentials provided are wrong or access denied")
                return False

            # 3️⃣ Fallback (status 200 usually means login page again)
            print("Credentials provided are wrong...")
            return False

        except Exception as e:
            print(f"[-] Login Exception: {e}")
            return False

    def extract_urls(self, base_url: str, html: str) -> set[str]:
        soup = BeautifulSoup(html, "html.parser")
        out = set()

        # tag -> attribute that commonly contains URLs
        url_attrs = [
            ("a", "href"),
            ("link", "href"),
            ("script", "src"),
            ("img", "src"),
            ("iframe", "src"),
            ("frame", "src"),
            ("source", "src"),
            ("video", "src"),
            ("audio", "src"),
            ("embed", "src"),
            ("object", "data"),
            ("form", "action"),
            ("button", "formaction"),
            ("input", "formaction"),
        ]

        # 1) Normal URL-bearing attributes
        for tag, attr in url_attrs:
            for el in soup.find_all(tag):
                v = el.get(attr)
                if not v:
                    continue
                v = v.strip()

                # ignore non-navigation schemes / fragments
                if v.startswith(("javascript:", "#", "mailto:", "tel:")):
                    continue

                out.add(urljoin(base_url, v))

        # 2) Meta refresh: <meta http-equiv="refresh" content="0;url=/path">
        for m in soup.find_all("meta"):
            if (m.get("http-equiv") or "").lower() == "refresh":
                content = m.get("content") or ""
                m2 = re.search(r"url\s*=\s*([^;]+)", content, flags=re.IGNORECASE)
                if m2:
                    v = m2.group(1).strip().strip("'\"")
                    if v and not v.startswith(("javascript:", "#")):
                        out.add(urljoin(base_url, v))

        # 3) Common data-* URL attributes (best-effort)
        for el in soup.find_all(True):
            for k, v in el.attrs.items():
                if not isinstance(v, str):
                    continue
                k = k.lower()
                if k in ("data-url", "data-href", "data-src", "data-action"):
                    vv = v.strip()
                    if vv and not vv.startswith(("javascript:", "#")):
                        out.add(urljoin(base_url, vv))

        return out

    def crawl(self):
        """The Main Loop"""
        if not self.login():
            return

        # Start crawling at the index
        start_node = self.url
        self.queue.append(start_node)
        
        print(f"[*] Starting Authenticated Crawl...")
        
        while self.queue:
            url = self.queue.pop(0)
            if url in self.visited:
                continue

            try:
                print(f"   Crawling: {url}")
                r = self.session.get(url)
                self.visited.add(url)
                
                discovered = self.extract_urls(url, r.text)
                for full_url in discovered:
                    if self.in_scope(full_url) and full_url not in self.visited:
                        self.queue.append(full_url)

                time.sleep(0.2) 

            except Exception as e:
                print(f"   Error crawling {url}: {e}")

if __name__ == "__main__":

    # before crawling, checks if the website requires authentication/a session cookie  
    # if requires authenticated session, ask for credentials and the endpoint
    # domain_to_crawl = input("Domain to crawl: ").strip()

    ##########################################################################################
    username = "test"
    password = "test"
    login_endpoint = "/login" # change to the exact login endpoint of the website
    # change the payload to how to website accepts

    auth_info = {
        "login_payload": {
            "username": username,
            "password": password,
            # "Login": "Login",
            "token_required": False,
            # "token_name": "user_token"
        },
        "login_endpoint": login_endpoint
    }
    origin_url = "http://127.0.0.1:5000" # change to whichever website to crawl
    ###########################################################################################

    bot = AuthenticatedCrawler(
        origin_url=origin_url,
        auth_info=auth_info
    )
    bot.crawl()