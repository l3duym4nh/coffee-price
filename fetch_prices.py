import urllib.request
import json
import re
import os
from datetime import datetime

GH_TOKEN = os.environ.get('GH_TOKEN', '')

def main():
    req = urllib.request.Request(
        "https://giacaphe.com/",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        html = response.read().decode('utf-8', errors='ignore')

    vietnam_match = re.search(r"Giá cà phê ngày (\d{2}/\d{2}/\d{4})", html)
    trungbinh_match = re.search(r"Trung bình.*?data-cur=\"([\d.]+)\"", html)
    robusta_match = re.search(r"data-thi-truong='RC'.*?data-price='([\d.]+)'", html)
    arabica_match = re.search(r"data-thi-truong='KC'.*?data-price='([\d.]+)'", html)

    vietnam_date = vietnam_match.group(1) if vietnam_match else None
    vietnam = int(float(trungbinh_match.group(1))) if trungbinh_match else None
    robusta = int(float(robusta_match.group(1))) if robusta_match else None
    arabica = float(arabica_match.group(1)) if arabica_match else None

    print(f"Date: {vietnam_date}")
    print(f"Vietnam: {vietnam}")
    print(f"Robusta: {robusta}")
    print(f"Arabica: {arabica}")

    existing = {"history": []}
    
    if GH_TOKEN:
        gist_req = urllib.request.Request(
            "https://api.github.com/gists/d4d3e60a5fa00da0a7ee0128ac577304",
            headers={"Authorization": f"Token {GH_TOKEN}", "User-Agent": "CoffeePriceBot"}
        )
        try:
            with urllib.request.urlopen(gist_req, timeout=30) as response:
                gist_data = json.loads(response.read())
                files = gist_data.get("files", {})
                if "prices.json" in files:
                    content = files["prices.json"].get("content", '{"history":[]}')
                    existing = json.loads(content)
        except Exception as e:
            print(f"Could not fetch Gist: {e}")
    else:
        print("GH_TOKEN not set, will create new file")

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
        
        with open("updated_prices.json", "w") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        print("Saved to updated_prices.json")
    else:
        print("No valid price data found on page")
        if vietnam_date:
            # Save even if no prices, for debugging
            with open("updated_prices.json", "w") as f:
                json.dump({"history": [], "lastUpdate": None}, f)

if __name__ == "__main__":
    main()
