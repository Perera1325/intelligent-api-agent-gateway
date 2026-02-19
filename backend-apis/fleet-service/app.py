from flask import Flask, jsonify, request
import json
import datetime
import logging

app = Flask(__name__)

# Structured logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def load_vehicles():
    with open("vehicles.json", "r") as file:
        return json.load(file)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Fleet Service",
        "status": "Running",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "Fleet Service",
        "status": "healthy"
    })


@app.route("/fleet/available", methods=["GET"])
def get_available_vehicles():
    required_capacity = request.args.get("capacity")

    if not required_capacity:
        return jsonify({"error": "Capacity parameter required"}), 400

    required_capacity = int(required_capacity)
    vehicles = load_vehicles()

    available = [
        v for v in vehicles
        if v["status"] == "available" and v["capacity_kg"] >= required_capacity
    ]

    logging.info(f"Capacity requested: {required_capacity}")
    logging.info(f"Vehicles matched: {len(available)}")

    return jsonify({
        "requested_capacity": required_capacity,
        "available_vehicles": available,
        "generated_at": datetime.datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
