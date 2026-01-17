import requests
import json
import re
import html
from urllib.parse import urlparse

class Shopify500Scraper:
    def __init__(self, target_stores, output_file="500_products.json"):
        # Ensure we only have 5 stores
        self.targets = target_stores[:5]
        self.output_file = output_file
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        self.master_list = []

    def _clean_text(self, raw_html):
        """Strips HTML tags for clean text."""
        if not raw_html: return ""
        text = html.unescape(raw_html)
        text = re.sub(r'<[^>]+>', ' ', text)
        return " ".join(text.split())

    def normalize(self, p, domain):
        """Format the data into the strict JSON schema."""
        # Get price from first variant
        variants = p.get('variants', [])
        price = variants[0].get('price') if variants else "0.00"
        
        # Get main image
        images = p.get('images', [])
        image_src = images[0].get('src') if images else None

        return {
            "id": p.get("id"),
            "store_domain": domain,
            "title": p.get("title"),
            "handle": p.get("handle"),
            "url": f"https://{domain}/products/{p.get('handle')}",
            "price": price,
            "currency": "USD", # Standard Assumption for these US stores
            "image": image_src,
            "vendor": p.get("vendor"),
            "description": self._clean_text(p.get("body_html"))
        }

    def fetch_store_products(self, domain):
        """Fetches EXACTLY 100 products from a store."""
        # limit=100 ensures we get exactly 100 items in one shot
        url = f"https://{domain}/products.json?limit=100"
        
        try:
            print(f"--> Fetching 100 items from: {domain}...")
            r = self.session.get(url, timeout=10)
            
            if r.status_code != 200:
                print(f"    [Error] Status {r.status_code}")
                return []
                
            data = r.json()
            raw_products = data.get('products', [])
            
            # Strict slice to ensure exactly 100 (in case store returns more)
            return raw_products[:100]
            
        except Exception as e:
            print(f"    [Exception] {e}")
            return []

    def run(self):
        print(f"--- Starting 5x100 Scrape ---")
        
        for domain in self.targets:
            # 1. Fetch raw data
            products = self.fetch_store_products(domain)
            
            # 2. Normalize and append
            for p in products:
                clean_item = self.normalize(p, domain)
                self.master_list.append(clean_item)
                
            print(f"    [Success] Added {len(products)} products.")

        # 3. Save to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.master_list, f, indent=2, ensure_ascii=False)
            
        print(f"\n[DONE] Saved {len(self.master_list)} products to {self.output_file}")

# --- EXECUTION ---
if __name__ == "__main__":
    # 5 Diverse Stores (Fashion, Tech, Home, Beauty, Accessories)
    target_shops = [
        "kith.com",             # Streetwear
        "nomadgoods.com",       # Tech Accessories
        "brooklinen.com",       # Home Goods
        "colourpop.com",        # Beauty/Cosmetics
        "gymshark.com"          # Fitness Apparel
    ]
    
    scraper = Shopify500Scraper(target_shops)
    scraper.run()