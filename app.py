import os
import sqlite3
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, send_from_directory, session, url_for, request
from authlib.integrations.flask_client import OAuth
import Dabas
import OpenFoodFacts
import EnvironmentalDataAPI
import cleansing
import lookupIngredients

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        user_id TEXT NOT NULL,
        barcode TEXT NOT NULL,
        UNIQUE(user_id, barcode)
    )
    """)

    conn.commit()
    conn.close()

init_db()

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
    off_result = OpenFoodFacts.getProduct(barcode)

    data = {}

    if not dabas_result and not off_result:
        return jsonify({"error": "Produkt hittades inte"}), 404

    if dabas_result:
        data["name"] = dabas_result.get("Hyllkantstext", "Okänt namn")
        data["brand"] = dabas_result.get("Varumarke", {}).get("Varumarke", "Okänt märke")
        data["raw_ingredients"] = dabas_result.get("Ingrediensforteckning", "Okända ingredienser")
        data["ingredients"] = cleansing.correct_ingredient(data["raw_ingredients"])
        data["source"] = "DABAS"

    if off_result:
        env_data = EnvironmentalDataAPI.getProductEnvironmentalData(off_result)
        product = off_result["product"]
        
        data["ecoscore_grade"] = env_data.get("ecoscore_grade", "?")
        data["ecoscore_score"] = env_data.get("ecoscore_score", "?")
        data["category"] = env_data.get("agribalyse", {}).get("name_en", "?")
        data["source"] = "DABAS + OpenFoodFacts"

        if not dabas_result:
            data["source"] = "OpenFoodFacts"
            data["name"] = product.get("product_name", "Okänt namn")
            data["brand"] = product.get("brands", "Okänt märke")
            data["raw_ingredients"] = product.get("ingredients_text", "Okända ingredienser")
            data["ingredients"] = cleansing.correct_ingredient(data["raw_ingredients"])

    warnings = lookupIngredients.match_ingredients(data["ingredients"])
    for warning in warnings:
        msg = f"{warning.get("standard_name")}: {warning.get("risk_reason")}\n"
        data.setdefault("warnings", []).append(msg)

    return jsonify({
        "source": data.get("source", "Unknown"),
        "name": data.get("name", "Unknown"),
        "ingredients": data.get("ingredients", "Unknown"),
        "brand": data.get("brand", "Unknown"),
        "ecoscore_grade": data.get("ecoscore_grade", "Unknown"),
        "ecoscore_score": data.get("ecoscore_score", "Unknown"),
        "category": data.get("category", "Unknown"),
        "warnings": data.get("warnings", [])
    })

@app.route("/api/favorites")
def get_favorites():

    user = session.get("user")

    if not user:
        return jsonify([]), 401

    user_id = user["sub"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT barcode FROM favorites WHERE user_id = ?",
        (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    favorites = [row[0] for row in rows]

    return jsonify(favorites)


@app.route("/api/favorites", methods=["POST"])
def add_favorite():

    user = session.get("user")

    if not user:
        return jsonify({"error": "Not logged in"}), 401

    user_id = user["sub"]

    data = request.get_json()
    barcode = data["barcode"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO favorites (user_id, barcode) VALUES (?, ?)",
        (user_id, barcode)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/api/favorites/<barcode>", methods=["DELETE"])
def remove_favorite(barcode):

    user = session.get("user")

    if not user:
        return jsonify({"error": "Not logged in"}), 401

    user_id = user["sub"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM favorites WHERE user_id = ? AND barcode = ?",
        (user_id, barcode)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})


if __name__ == "__main__":
    #demo()
    app.run(debug=True)
