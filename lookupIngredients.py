import json
import os

def matchIngredients(ingredients):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'harmfulingredients.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        harmful_data = json.load(f)
        
    matched_ingredients = []
    
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()
        
        for item in harmful_data:
            for term in item.get('search_terms', []):
                if term in ingredient_lower:
                    if item not in matched_ingredients:
                        matched_ingredients.append(item)
                    break
                    
    return matched_ingredients