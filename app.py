from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# ✅ ENABLE CORS (THIS IS THE MAIN FIX)
CORS(app)

@app.route("/")
def home():
    return jsonify({
        "message": "Backend is running successfully"
    })

if __name__ == "__main__":
    app.run()

