import urllib.request
import json
import re
import os
import ssl
from datetime import datetime

GH_TOKEN = os.environ.get('GH_TOKEN', '')
GIST_ID = 'd4d3e60a5fa00da0a7ee0128ac577304'

def create_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def update_gist(data):
    if not GH_TOKEN:
        print("GH_TOKEN not set, cannot update Gist")
        return False
    
    payload = {
        "files": {
            "prices.json": {
                "content": json.dumps(data, indent=2, ensure_ascii=False)
            }
        }
    }
    
    req = urllib.request.Request(
        f"https://api.github.com/gists/{GIST_ID}",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Token {GH_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "CoffeePriceBot"
        },
        method="PATCH"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30, context=create_ssl_context()) as response:
            result = json.loads(response.read())
            print(f"Gist updated: {result.get('html_url', 'OK')}")
            return True
    except Exception as e:
        print(f"Gist update error: {e}")
        return False

def main():
    req = urllib.request.Request(
        "https://giacaphe.com/",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        html = response.read().decode('utf-8', errors='ignore')

    vietnam_match = re.search(r"Giá cà phê ngày (\d{2}/\d{2}/\d{4})", html)
    trungbinh_match = re.search(r"data-cur=\"([\d.]+)\"", html)
    
    robusta_section = re.search(r"data-thi-truong='RC'.*?</tr>", html, re.DOTALL)
    robusta_match = re.search(r"data-price='([\d.]+)'", robusta_section.group()) if robusta_section else None
    
    arabica_section = re.search(r"data-thi-truong='KC'.*?</tr>", html, re.DOTALL)
    arabica_match = re.search(r"data-price='([\d.]+)'", arabica_section.group()) if arabica_section else None

    vietnam_date = vietnam_match.group(1) if vietnam_match else None
    vietnam = int(float(trungbinh_match.group(1))) if trungbinh_match else None
    robusta = int(float(robusta_match.group(1))) if robusta_match else None
    arabica = float(arabica_match.group(1)) if arabica_match else None

    print(f"Date: {vietnam_date}")
    print(f"Vietnam: {vietnam}")
    print(f"Robusta: {robusta}")
    print(f"Arabica: {arabica}")

    existing: dict = {"history": []}
    
    if GH_TOKEN:
        gist_req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"Token {GH_TOKEN}", "User-Agent": "CoffeePriceBot"}
        )
        try:
            with urllib.request.urlopen(gist_req, timeout=30, context=create_ssl_context()) as response:
                gist_data = json.loads(response.read())
                files = gist_data.get("files", {})
                if "prices.json" in files:
                    content = files["prices.json"].get("content", '{"history":[]}')
                    existing = json.loads(content)
                    print(f"Loaded existing data with {len(existing.get('history', []))} entries")
        except Exception as e:
            print(f"Could not fetch Gist: {e}")

    if vietnam and robusta:
        new_price = {
            "timestamp": int(datetime.now().timestamp()),
            "date": vietnam_date,
            "vietnam": vietnam,
            "robusta": robusta,
            "arabica": arabica
        }
        
        dates = [h.get("date") for h in existing.get("history", [])]
        if vietnam_date not in dates:
            existing["history"].append(new_price)
            print(f"Added new price for {vietnam_date}")
        else:
            for i, h in enumerate(existing["history"]):
                if h.get("date") == vietnam_date:
                    existing["history"][i] = new_price
                    print(f"Updated price for {vietnam_date}")
                    break
        
        if len(existing["history"]) > 30:
            existing["history"] = existing["history"][-30:]
        
        existing["lastUpdate"] = datetime.now().isoformat()
        
        update_gist(existing)
    else:
        print("No valid price data found on page")

if __name__ == "__main__":
    main()
