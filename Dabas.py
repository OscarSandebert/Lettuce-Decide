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

    if response.status_code == 200:
        return response.json()
    else:
        print("Error", response.status_code)
        return None
    
product = getProduct("07310867502214")
print(product)

