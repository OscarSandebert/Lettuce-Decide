from flask import Flask, jsonify, send_from_directory
import Dabas
import OpenFoodFacts
import EnvironmentalDataAPI
import cleansing

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")

def demo():
    gtin = input("Enter GTIN: ")
    print(lookup(gtin))

@app.route("/api/lookup/<barcode>")
def lookup(barcode):
    if len(barcode) == 13 and not barcode.startswith("0"):
        barcode = "0" + barcode
    elif len(barcode) == 14 and not barcode.startswith("0"):
        barcode = "0" + barcode[1:]
    
    dabas_result = Dabas.getProduct(barcode)
    if dabas_result:
        name = dabas_result.get("Hyllkantstext", "Okänt namn")
        brand = dabas_result.get("Varumarke", {}).get("Varumarke", "Okänt märke")
        raw_ingredients = dabas_result.get("Ingrediensforteckning", "Okända ingredienser")
        ingredients = cleansing.correct_ingredient(raw_ingredients)
        return jsonify({
            "source": "DABAS",
            "name": name,
            "brand": brand,
            "raw_ingredients": raw_ingredients,
            "ingredients": ingredients
        })

    off_result = OpenFoodFacts.getProduct(barcode)
    if off_result:
        env_data = EnvironmentalDataAPI.getProductEnvironmentalData(off_result)
        product = off_result["product"]
        name = product.get("product_name", "Okänt namn")
        brand = product.get("brands", "Okänt märke")
        raw_ingredients = product.get("ingredients_text", "Okända ingredienser")
        ingredients = cleansing.correct_ingredient(raw_ingredients)
        ecoscore_grade = env_data.get("ecoscore_grade", "?")
        ecoscore_score = env_data.get("ecoscore_score")
        category = env_data.get("agribalyse", {}).get("name_en", "?")
        return jsonify({
            "source": "OpenFoodFacts",
            "name": name,
            "brand": brand,
            "ecoscore_grade": ecoscore_grade,
            "ecoscore_score": ecoscore_score,
            "category": category
        })

    return jsonify({"error": "Produkt hittades inte"}), 404


if __name__ == "__main__":
    #demo()
    app.run(debug=True)
