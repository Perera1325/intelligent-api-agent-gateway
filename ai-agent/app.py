from flask import Flask, request, jsonify
import requests
import json
import datetime
import logging
import time

app = Flask(__name__)

# =========================================================
# CONFIGURATION
# =========================================================

API_KEY = "vinod-secure-key"
CACHE_TTL = 60  # seconds
cache = {}

metrics = {
    "total_requests": 0,
    "cache_hits": 0,
    "agent_executions": 0
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# =========================================================
# LOAD SERVICE REGISTRY
# =========================================================

def load_registry():
    with open("../service-registry.json", "r") as file:
        return json.load(file)

registry = load_registry()

# =========================================================
# AUTHENTICATION
# =========================================================

def authenticate(req):
    key = req.headers.get("x-api-key")
    return key == API_KEY

# =========================================================
# SAFE SERVICE CALL (Retry + Timeout)
# =========================================================

def safe_call_service(url, retries=2, timeout=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.warning(f"Attempt {attempt+1} failed for {url}: {str(e)}")
            time.sleep(1)

    return {"error": "Service unavailable"}

# =========================================================
# INTELLIGENT DECISION ENGINE (Stable Version)
# =========================================================

def intelligent_decision(weather, traffic, fleet, city, capacity):

    explanation = []
    decision = "Proceed with delivery"

    if "error" in weather:
        explanation.append("Weather service unavailable.")

    if "error" in traffic:
        explanation.append("Traffic service unavailable.")

    if "error" in fleet:
        explanation.append("Fleet service unavailable.")

    if traffic.get("congestion_level") in ["High", "Severe"]:
        decision = "Delay delivery"
        explanation.append("High traffic congestion detected.")

    if weather.get("condition") == "Stormy":
        decision = "Delay delivery"
        explanation.append("Severe weather conditions.")

    if not fleet.get("available_vehicles") and "error" not in fleet:
        decision = "Delivery not possible"
        explanation.append("No available vehicles with required capacity.")

    if not explanation:
        explanation.append("All systems normal.")

    return {
        "decision": decision,
        "explanation": explanation
    }

# =========================================================
# ROOT
# =========================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "AI Agent Orchestrator (Stable Mode)",
        "status": "Running",
        "timestamp": datetime.datetime.now().isoformat()
    })

# =========================================================
# HEALTH
# =========================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "AI Agent",
        "status": "healthy"
    })

# =========================================================
# METRICS
# =========================================================

@app.route("/metrics", methods=["GET"])
def get_metrics():
    return jsonify(metrics)

# =========================================================
# MAIN AGENT ENDPOINT
# =========================================================

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

    # CACHE CHECK
    if cache_key in cache:
        cached_data, timestamp = cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            metrics["cache_hits"] += 1
            logging.info("Cache hit")
            return jsonify(cached_data)

    metrics["agent_executions"] += 1

    # CALL SERVICES
    weather_url = registry["weather_service"]["base_url"] + registry["weather_service"]["endpoint"]
    traffic_url = registry["traffic_service"]["base_url"] + registry["traffic_service"]["endpoint"] + f"?city={city}"
    fleet_url = registry["fleet_service"]["base_url"] + registry["fleet_service"]["endpoint"] + f"?capacity={capacity}"

    weather_data = safe_call_service(weather_url)
    traffic_data = safe_call_service(traffic_url)
    fleet_data = safe_call_service(fleet_url)

    # INTELLIGENT DECISION
    decision_result = intelligent_decision(weather_data, traffic_data, fleet_data, city, capacity)

    response_data = {
        "input": {
            "city": city,
            "capacity": capacity
        },
        "weather": weather_data,
        "traffic": traffic_data,
        "fleet": fleet_data,
        "agent_decision": decision_result,
        "generated_at": datetime.datetime.now().isoformat()
    }

    # STORE CACHE
    cache[cache_key] = (response_data, time.time())

    logging.info("Agent execution completed")

    return jsonify(response_data)

# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
