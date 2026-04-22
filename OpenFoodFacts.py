import requests
import json

def getProductEnvironmentalData(data):
        product = data["product"]
        
        eco_data = product.get("ecoscore_data", {})
        
        result = {
            "name": product.get("product_name", "Okänt namn"),
            "ecoscore_grade": product.get("ecoscore_grade", "unknown"),
            "ecoscore_score": product.get("ecoscore_score"),
            "agribalyse": eco_data.get("agribalyse", {}),
        }

        return result

# TESTA KODEN
res = getProductEnvironmentalData("5000181028133")

if res:
    #print(f"Produkt: {res['name']}")
    print(f"Eco-Score: {res['ecoscore_grade'].upper()}")
    
    # Skriv ut agribalyse-datan snyggt (detta ersätter [Object] i konsolen)
    print("\n--- Detaljerad miljödata (Agribalyse) ---")
    print(json.dumps(res['agribalyse'], indent=2, ensure_ascii=False))