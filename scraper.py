import json
import os
import re # Add this import
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Define target products and their web elements
# Replace these URLs and CSS selectors with your actual target products
PRODUCTS = [
    {
        "id": "item-3",
        "brand": "MyProtein",
        "name": "Impact Whey Protein (2.2 lb / 1kg)",
        "url": "https://www.myprotein.co.in/p/sports-nutrition/impact-whey-protein/11654605/?variation=15418484",
        "selector": ".price",
        "fallback_price": "$913.99"
    }
]

def extract_price(url, selector, fallback):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # Force UTF-8 encoding to help with the Rupee symbol
        response.encoding = 'utf-8' 
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        element = soup.select_one(selector)
        
        if element:
            raw_text = element.get_text(strip=True)
            
            # Use regex to extract only the numeric value (ignores hidden marks and broken symbols)
            match = re.search(r'[0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?', raw_text)
            if match:
                clean_number = match.group(0).replace(',', '')
                return f"₹{clean_number}" # Manually prepend the clean Rupee symbol
                
            return raw_text
    except Exception as error:
        print(f"Scraping failed for {url}: {error}")
        return fallback

def run_tracker():
    today = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    current_records = []

    for item in PRODUCTS:
        price = extract_price(item["url"], item["selector"], item["fallback_price"])
        current_records.append({
            "id": item["id"],
            "brand": item["brand"],
            "name": item["name"],
            "price": price,
            "url": item["url"],
            "last_updated": today
        })

    # Save to prices.json
    output_payload = {
        "last_synced": today,
        "items": current_records
    }

    with open("prices.json", "w", encoding="utf-8") as file:
        json.dump(output_payload, file, indent=2, ensure_ascii=False)
    
    print(f"Successfully updated prices.json with {len(current_records)} items.")

if __name__ == "__main__":
    run_tracker()
