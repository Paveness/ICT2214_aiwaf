import requests
import re
import json
import time
import random
import string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote_plus
from pathlib import Path

# ==========================================
# PART 1: The Crawler & Form Analyzer
# ==========================================
class SmartCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.site_map = {}  # Stores { url: { "forms": [] } }
        self.session = requests.Session()
        # Set a browser user-agent
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (NeuroWAF-Training-Bot)"
        })

    def extract_forms(self, url, soup):
        """Finds all forms and their input fields on a page."""
        forms_found = []
        for form in soup.find_all("form"):
            action = form.get("action") or url
            method = (form.get("method") or "GET").upper()
            full_action = urljoin(url, action)
            
            inputs = []
            for inp in form.find_all(["input", "textarea", "select"]):
                name = inp.get("name")
                if name:
                    inputs.append(name)
            
            forms_found.append({
                "action": full_action,
                "method": method,
                "inputs": inputs
            })
        return forms_found

    def crawl(self):
        print(f"[*] Starting Intelligence Crawl on {self.base_url}...")
        queue = [self.base_url]
        
        while queue:
            url = queue.pop(0)
            if url in self.visited: continue
            
            try:
                # 1. Fetch Page
                res = self.session.get(url, timeout=3)
                self.visited.add(url)
                
                # 2. Parse Content
                soup = BeautifulSoup(res.text, "html.parser")
                
                # 3. Learn Forms (The key part!)
                forms = self.extract_forms(url, soup)
                self.site_map[url] = {"forms": forms}
                
                if forms:
                    print(f"    [+] Found {len(forms)} form(s) on {url}: {[f['inputs'] for f in forms]}")

                # 4. Find new links to crawl
                for a in soup.find_all("a", href=True):
                    next_url = urljoin(url, a["href"])
                    # Only stay within scope (localhost)
                    if urlparse(next_url).netloc == urlparse(self.base_url).netloc:
                        if next_url not in self.visited and next_url not in queue:
                            queue.append(next_url)
                            
                time.sleep(0.1) # Be gentle

            except Exception as e:
                print(f"    [-] Failed to crawl {url}: {e}")

        print(f"[*] Map complete. Discovered {len(self.site_map)} pages.")
        return self.site_map

# ==========================================
# PART 2: The Data Generator (Uses the Map)
# ==========================================
class DatasetGenerator:
    def __init__(self, site_map):
        self.site_map = site_map
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        ]

    def _generate_value(self, field_name):
        """Smart value generation based on field names."""
        name = field_name.lower()
        if "user" in name: return f"user_{random.randint(100,999)}"
        if "pass" in name: return "SecureP@ss123"
        if "mail" in name: return f"test{random.randint(1,100)}@example.com"
        if "search" in name or "q" == name: return random.choice(["books", "hacking", "AI", "security"])
        if "id" in name: return str(random.randint(1, 10))
        if "ip" in name: return f"192.168.1.{random.randint(1,255)}"
        if "comment" in name or "desc" in name: 
            words = ["Great", "Book", "Terrible", "Amazing", "WAF", "Testing"]
            return " ".join(random.choices(words, k=5))
        return "dummy_data"

    def extract_features(self, method, url, body, headers):
        """
        Duplicate of your WAF's feature extraction logic to ensure compatibility.
        """
        # (This must match your ai_features.py logic exactly)
        _SUSPICIOUS = set(string.punctuation)
        _HEX_RE = re.compile(r"%[0-9a-fA-F]{2}")
        
        parsed = urlparse(url)
        path = parsed.path
        query = parsed.query
        
        decoded_path = unquote_plus(path)
        
        feat = {
            "method": method,
            "raw_path_len": len(path),
            "decoded_path_len": len(decoded_path),
            "normalized_path_len": len(path), # Simplified for gen
            "path_slash_count": path.count("/"),
            "path_dot_count": path.count("."),
            "path_pct_count": path.count("%"),
            "path_hex_pct_count": len(_HEX_RE.findall(path)),
            "query_len": len(query),
            "query_pct_count": query.count("%"),
            "query_hex_pct_count": len(_HEX_RE.findall(query)),
            "query_amp_count": query.count("&"),
            "query_eq_count": query.count("="),
            "query_suspicious_char_count": sum(1 for c in unquote_plus(query) if c in _SUSPICIOUS),
            "path_suspicious_char_count": sum(1 for c in decoded_path if c in _SUSPICIOUS),
            "header_count": len(headers),
            "has_cookie": 1 if "cookie" in headers else 0,
            "ua_len": len(headers.get("user-agent", "")),
            "ct_len": len(headers.get("content-type", "")),
            "body_len": len(body),
            "body_pct_count": body.count("%"),
            "body_hex_pct_count": len(_HEX_RE.findall(body)),
            "body_suspicious_char_count": sum(1 for c in body if c in _SUSPICIOUS),
            "body_alpha_count": sum(1 for c in body if c.isalpha()),
            "body_digit_count": sum(1 for c in body if c.isdigit()),
            "ct_is_json": 1 if "json" in headers.get("content-type", "") else 0,
            "ct_is_form": 1 if "form" in headers.get("content-type", "") else 0,
        }
        return feat

    def generate_single(self):
        # Pick a random page we discovered
        url, data = random.choice(list(self.site_map.items()))
        forms = data["forms"]

        # Decision: Browse (GET) or Interact (POST)?
        # If forms exist, 30% chance to submit one.
        if forms and random.random() < 0.3:
            form = random.choice(forms)
            method = form["method"]
            target_url = form["action"]
            
            # Fill the form
            payload_parts = []
            for field in form["inputs"]:
                val = self._generate_value(field)
                payload_parts.append(f"{field}={val}")
            
            body = "&".join(payload_parts)
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": random.choice(self.user_agents)
            }
        else:
            # Just viewing the page
            method = "GET"
            target_url = url
            body = ""
            headers = {"user-agent": random.choice(self.user_agents)}

        return self.extract_features(method, target_url, body, headers)

# ==========================================
# PART 3: Execution
# ==========================================
if __name__ == "__main__":
    # 1. CRAWL (The Map Phase)
    # Ensure your shop_app.py is running on port 5000!
    crawler = SmartCrawler("http://127.0.0.1:5000")
    site_map = crawler.crawl()

    if not site_map:
        print("[-] No pages found! Is the server running?")
        exit(1)

    # 2. GENERATE (The Training Phase)
    generator = DatasetGenerator(site_map)
    output_file = Path("app/ai_models/data/ai_requests.jsonl")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    LIMIT = 20000 # Start small to test, then increase to 1,000,000
    print(f"[*] Generating {LIMIT} training records based on crawled data...")
    
    with open(output_file, "w") as f:
        for i in range(LIMIT):
            feat = generator.generate_single()
            row = {
                "ts": time.time(),
                "label": "baseline",
                "features": feat
            }
            f.write(json.dumps(row) + "\n")
            
            if i % 5000 == 0 and i > 0:
                print(f"    ... {i} records generated")
                
    print(f"[+] Done! Saved to {output_file}")