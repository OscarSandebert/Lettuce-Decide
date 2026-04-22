import requests

def getProduct(gtin):

    url = f'https://world.openfoodfacts.org/api/v0/product/{gtin}.json'

    headers = {
        "User-Agent": "TestApp/1.0 (test@example.com)"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Error", response.status_code)
        return None

    data = response.json()
    if data.get("status") == 0:
        print("Error: Product not found")
        return None

    return data
    
#pb = getProduct("737628064502")
#print(pb)