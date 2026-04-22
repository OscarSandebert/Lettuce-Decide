"""
Funkar inte än, väntar på svar från Dabas med API key
"""


import requests

def getProduct(gtin):
    url = f'https://api.dabas.com/DABASService/V2/article/gtin/{gtin}/json'
    
    headers = {
        "Authorization": f'Bearer YOUR_API_KEY'
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
    
#product = getProduct("07310867502214")
#print(product)

