from flask import Flask, jsonify
import random
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "SpeedCheckPlus Backend is Live"

@app.route("/speedtest")
def speedtest():
    return jsonify({
        "download": round(random.uniform(20, 80), 2),
        "upload": round(random.uniform(10, 30), 2),
        "ping": round(random.uniform(5, 50), 2)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
