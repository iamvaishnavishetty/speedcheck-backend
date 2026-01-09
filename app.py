from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({
        "message": "Backend is running successfully",
        "download_speed": "92 Mbps",
        "upload_speed": "41 Mbps",
        "ping": "12 ms"
    })

if __name__ == "__main__":
    app.run()
