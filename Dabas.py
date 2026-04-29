from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv("DABAS_API_KEY")

def getProduct(gtin):
    url = f'https://api.dabas.com/DABASService/V2/article/gtin/{gtin}/json'
    params = {"apikey": api_key}
    
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Error", response.status_code)
        return None

    data = response.json()
    if data.get("status") == 0:
        print("Error: Product not found")
        return None

    return data
    
#product = getProduct("07310867502214")
#print(product)

