from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

# Flask app setup
app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb://mongo:27017")
db = client["logging_db"]
log_collection = db["logs"]

# Endpoint to receive logs
@app.post("/log")
def log_entry():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Invalid log data"}), 400

    # Add timestamp to the log
    data["timestamp"] = datetime.utcnow()
    log_collection.insert_one(data)

    return jsonify({"message": "Log entry saved"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
