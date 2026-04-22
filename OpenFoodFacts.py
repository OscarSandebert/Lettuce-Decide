import requests

def getProduct(gtin):
 
    url = f'https://world.openfoodfacts.org/api/v0/product/{gtin}.json'

    headers = {
        "User-Agent": "TestApp/1.0 (test@example.com)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error", response.status_code)
        return None
    
pb = getProduct("737628064502")
print(pb)