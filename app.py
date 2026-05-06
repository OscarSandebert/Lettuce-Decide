from flask import Flask, jsonify, send_from_directory
import Dabas
import OpenFoodFacts
import EnvironmentalDataAPI

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/lookup/<barcode>")
def lookup(barcode):
    if len(barcode) == 12 and not barcode.startswith("0"):
        barcode = "0" + barcode
    elif len(barcode) == 13 and not barcode.startswith("0"):
        barcode = "0" + barcode[1:]
    result = Dabas.getProduct(barcode)
    if result is not None:
        return jsonify({
            "source": "DABAS",
            "name": result.get("Hyllkantstext", "Okänt namn"),
            "brand": result.get("Varumarke", {}).get("Varumarke", "Okänt märke"),
        })

    result = OpenFoodFacts.getProduct(barcode)
    if result is not None:
        env_data = EnvironmentalDataAPI.getProductEnvironmentalData(result)
        product = result["product"]
        return jsonify({
            "source": "OpenFoodFacts",
            "name": product.get("product_name", "Okänt namn"),
            "brand": product.get("brands", "Okänt märke"),
            "ecoscore_grade": env_data.get("ecoscore_grade", "?"),
            "ecoscore_score": env_data.get("ecoscore_score"),
            "category": env_data.get("agribalyse", {}).get("name_en", ""),
        })

    return jsonify({"error": "Produkt hittades inte"}), 404


if __name__ == "__main__":
    app.run(debug=True)
