import os
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, send_from_directory, session, url_for
from authlib.integrations.flask_client import OAuth
import Dabas
import OpenFoodFacts
import EnvironmentalDataAPI
import cleansing

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")

oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/logo.png")
def logo():
    return send_from_directory(".", "Lettuce Decide logo.png")


@app.route("/login")
def login():
    return oauth.google.authorize_redirect(url_for("auth_callback", _external=True))


@app.route("/auth/callback")
def auth_callback():
    token = oauth.google.authorize_access_token()
    userinfo = token.get("userinfo") or oauth.google.parse_id_token(token, nonce=None)
    session["user"] = {
        "sub": userinfo.get("sub"),
        "email": userinfo.get("email"),
        "name": userinfo.get("name"),
        "picture": userinfo.get("picture"),
    }
    return redirect(url_for("saved"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route("/api/me")
def me():
    user = session.get("user")
    if not user:
        return jsonify({"authenticated": False}), 401
    return jsonify({"authenticated": True, "user": user})


@app.route("/saved")
@login_required
def saved():
    return send_from_directory(".", "saved.html")


@app.route("/info")
def info():
    return send_from_directory(".", "info.html")

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
