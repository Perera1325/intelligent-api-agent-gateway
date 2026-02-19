from flask import Flask, request, jsonify
import requests
import json
import datetime
import logging
import time

app = Flask(__name__)

# ==============================
# CONFIG
# ==============================

API_KEY = "vinod-secure-key"

# Simple in-memory cache
cache = {}
CACHE_TTL = 60  # seconds

# Metrics
metrics = {
    "total_requests": 0,
    "cache_hits": 0,
    "agent_executions": 0
}

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ==============================
# LOAD SERVICE REGISTRY
# ==============================

def load_registry():
    with open("../service-registry.json", "r") as file:
        return json.load(file)

registry = load_registry()

# ==============================
# AUTH DECORATOR
# ==============================

def authenticate(request):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        return False
    return True

# ==============================
# ROOT
# ==============================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "AI Agent Orchestrator",
        "status": "Running",
        "timestamp": datetime.datetime.now().isoformat()
    })

# ==============================
# METRICS ENDPOINT
# ==============================

@app.route("/metrics", methods=["GET"])
def get_metrics():
    return jsonify(metrics)

# ==============================
# MAIN AGENT
# ==============================

@app.route("/agent/optimize-delivery", methods=["GET"])
def optimize_delivery():

    metrics["total_requests"] += 1

    if not authenticate(request):
        logging.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    city = request.args.get("city")
    capacity = request.args.get("capacity")

    if not city or not capacity:
        return jsonify({"error": "city and capacity required"}), 400

    cache_key = f"{city}-{capacity}"

    # ==============================
    # CHECK CACHE
    # ==============================
    if cache_key in cache:
        cached_data, timestamp = cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            metrics["cache_hits"] += 1
            logging.info("Cache hit")
            return jsonify(cached_data)

    metrics["agent_executions"] += 1

    # ==============================
    # CALL WEATHER
    # ==============================
    weather_url = registry["weather_service"]["base_url"] + registry["weather_service"]["endpoint"]
    weather_data = requests.get(weather_url).json()

    # ==============================
    # CALL TRAFFIC
    # ==============================
    traffic_url = (
        registry["traffic_service"]["base_url"] +
        registry["traffic_service"]["endpoint"] +
        f"?city={city}"
    )
    traffic_data = requests.get(traffic_url).json()

    # ==============================
    # CALL FLEET
    # ==============================
    fleet_url = (
        registry["fleet_service"]["base_url"] +
        registry["fleet_service"]["endpoint"] +
        f"?capacity={capacity}"
    )
    fleet_data = requests.get(fleet_url).json()

    # ==============================
    # INTELLIGENT DECISION
    # ==============================

    reasons = []
    recommendation = "Proceed with delivery"

    if traffic_data.get("congestion_level") in ["High", "Severe"]:
        recommendation = "Delay delivery"
        reasons.append("High traffic congestion")

    if weather_data.get("condition") == "Stormy":
        recommendation = "Delay delivery"
        reasons.append("Severe weather conditions")

    if not fleet_data.get("available_vehicles"):
        recommendation = "Delivery not possible"
        reasons.append("No available vehicles")

    response_data = {
        "input": {
            "city": city,
            "capacity": capacity
        },
        "weather": weather_data,
        "traffic": traffic_data,
        "fleet": fleet_data,
        "decision": recommendation,
        "explanation": reasons,
        "generated_at": datetime.datetime.now().isoformat()
    }

    # ==============================
    # STORE IN CACHE
    # ==============================

    cache[cache_key] = (response_data, time.time())

    logging.info("Agent execution completed")

    return jsonify(response_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
