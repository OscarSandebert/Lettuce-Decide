import Dabas
import OpenFoodFacts
import EnvironmentalDataAPI
import spellchecker

def get_user_input():
    input_ok = False
    while not input_ok:
        u_input = input('Enter GTIN: ')
        if u_input.isdigit():
            input_ok = True
        else:
            print('GTIN must be a number')
    return u_input

GTIN_input = get_user_input()

result = Dabas.getProduct(GTIN_input)
if result is None:
    print('Product not found in Dabas. Trying OpenFoodFacts')
    result = OpenFoodFacts.getProduct(GTIN_input)
    if result is None:
        print('Product could not be found in any database')
    else:
        print(result['product'].get('product_name', 'product name not found'))
        print(result['product'].get('brands', 'brand name not found'))
        raw_ingredients = result['product'].get('ingredients_text', 'ingredients not found')
        ingredients = spellchecker.correct_ingredient(raw_ingredients)
        print(ingredients)
        print(EnvironmentalDataAPI.getProductEnvironmentalData(result))
else:
    raw_ingredients = result.get('Ingrediensforteckning', 'ingredients not found')
    ingredients = spellchecker.correct_ingredient(raw_ingredients)
    print(ingredients)
    print(result.get('Hyllkantstext', 'product name not found'))
    print(result['Varumarke'].get('Varumarke', 'brand name not found'))