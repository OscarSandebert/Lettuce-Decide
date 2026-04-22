import requests
import json

def getProductEnvironmentalData(gtin):
    # Vi använder v2-API:et för bättre stöd av miljödata
    url = f'https://world.openfoodfacts.org/api/v2/product/{gtin}.json'

    headers = {
        # Använder din mail som User-Agent (bra praxis för OFF)
        "User-Agent": "lettuce-decide (oscar.sandebert@gmail.com)"
    }

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Fel vid anrop: {response.status_code}")
            return None

        data = response.json()
        
        if data.get("status") == 0 or "product" not in data:
            print("Error: Produkten hittades inte")
            return None

        product = data["product"]
        
        eco_data = product.get("ecoscore_data", {})
        
        result = {
            "name": product.get("product_name", "Okänt namn"),
            "ecoscore_grade": product.get("ecoscore_grade", "unknown"),
            "ecoscore_score": product.get("ecoscore_score"),
            "agribalyse": eco_data.get("agribalyse", {}),
        }

        return result

    except Exception as e:
        print(f"Ett oväntat fel uppstod: {e}")
        return None

# TESTA KODEN
res = getProductEnvironmentalData("5000181028133")

if res:
    #print(f"Produkt: {res['name']}")
    print(f"Eco-Score: {res['ecoscore_grade'].upper()}")
    
    # Skriv ut agribalyse-datan snyggt (detta ersätter [Object] i konsolen)
    print("\n--- Detaljerad miljödata (Agribalyse) ---")
    print(json.dumps(res['agribalyse'], indent=2, ensure_ascii=False))