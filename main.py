from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# Env vars or defaults
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "YOUR_DEFAULT_FINNHUB_KEY")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY", "YOUR_DEFAULT_TWELVE_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_DEFAULT_OPENROUTER_KEY")

FINNHUB_URL = "https://finnhub.io/api/v1/quote"
TWELVE_DATA_URL = "https://api.twelvedata.com/price"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def get_stock_price(symbol):
    try:
        r = requests.get(FINNHUB_URL, params={"symbol": symbol, "token": FINNHUB_API_KEY}, timeout=5)
        r.raise_for_status()
        data = r.json()
        if data.get("c"):
            return round(float(data["c"]), 2), "Finnhub"
    except Exception as e:
        print("[Finnhub] error:", e)

    try:
        r = requests.get(TWELVE_DATA_URL, params={"symbol": symbol, "apikey": TWELVE_DATA_API_KEY}, timeout=5)
        r.raise_for_status()
        data = r.json()
        if data.get("price"):
            return round(float(data["price"]), 2), "Twelve Data"
    except Exception as e:
        print("[TwelveData] error:", e)

    return None, None

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route("/price")
def price():
    symbol = request.args.get("symbol", "").strip().upper()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400

    price, source = get_stock_price(symbol)
    if price:
        return jsonify({"symbol": symbol, "price": price, "source": source})
    return jsonify({"error": f"Could not fetch price for {symbol}"}), 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"response": "Please enter a message."}), 400

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are a helpful investing assistant."},
            {"role": "user", "content": user_msg}
        ]
    }

    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=15)
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]
        return jsonify({"response": reply.strip()})
    except Exception as e:
        print("[OpenRouter] error:", e)
        return jsonify({"response": "Sorry, I couldn't get a response right now."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
