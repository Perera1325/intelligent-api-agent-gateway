from flask import Flask, request, jsonify, render_template
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
# CIRCUIT BREAKER CONFIG
# =========================================================

circuit_breakers = {
    "weather": {"failures": 0, "state": "CLOSED", "last_failure_time": None},
    "traffic": {"failures": 0, "state": "CLOSED", "last_failure_time": None},
    "fleet": {"failures": 0, "state": "CLOSED", "last_failure_time": None},
}

FAILURE_THRESHOLD = 3
COOLDOWN_TIME = 30  # seconds

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
# CIRCUIT BREAKER + SAFE SERVICE CALL
# =========================================================

def safe_call_service(service_name, url, retries=2, timeout=3):

    breaker = circuit_breakers[service_name]

    # If circuit is OPEN
    if breaker["state"] == "OPEN":
        if time.time() - breaker["last_failure_time"] < COOLDOWN_TIME:
            logging.warning(f"Circuit OPEN for {service_name}")
            return {"error": "Service temporarily disabled (circuit open)"}
        else:
            logging.info(f"Cooldown expired. Closing circuit for {service_name}")
            breaker["state"] = "CLOSED"
            breaker["failures"] = 0

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            breaker["failures"] = 0
            breaker["state"] = "CLOSED"

            return response.json()

        except Exception as e:
            logging.warning(f"{service_name} failed attempt {attempt+1}: {str(e)}")

    # All retries failed
    breaker["failures"] += 1
    breaker["last_failure_time"] = time.time()

    if breaker["failures"] >= FAILURE_THRESHOLD:
        breaker["state"] = "OPEN"
        logging.error(f"Circuit opened for {service_name}")

    return {"error": "Service unavailable"}

# =========================================================
# INTELLIGENT DECISION ENGINE
# =========================================================

def intelligent_decision(weather, traffic, fleet):

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
        explanation.append("All systems operating normally.")

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
        "service": "AI Agent Orchestrator",
        "status": "Running",
        "timestamp": datetime.datetime.now().isoformat()
    })

# =========================================================
# DASHBOARD ROUTE
# =========================================================

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")

# =========================================================
# HEALTH
# =========================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "AI Agent",
        "status": "healthy",
        "circuit_breakers": circuit_breakers
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
        return jsonify({"error": "Unauthorized"}), 401

    city = request.args.get("city")
    capacity = request.args.get("capacity")

    if not city or not capacity:
        return jsonify({"error": "city and capacity required"}), 400

    cache_key = f"{city}-{capacity}"

    # Check cache
    if cache_key in cache:
        cached_data, timestamp = cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            metrics["cache_hits"] += 1
            return jsonify(cached_data)

    metrics["agent_executions"] += 1

    weather_url = registry["weather_service"]["base_url"] + registry["weather_service"]["endpoint"]
    traffic_url = registry["traffic_service"]["base_url"] + registry["traffic_service"]["endpoint"] + f"?city={city}"
    fleet_url = registry["fleet_service"]["base_url"] + registry["fleet_service"]["endpoint"] + f"?capacity={capacity}"

    weather_data = safe_call_service("weather", weather_url)
    traffic_data = safe_call_service("traffic", traffic_url)
    fleet_data = safe_call_service("fleet", fleet_url)

    decision_result = intelligent_decision(weather_data, traffic_data, fleet_data)

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

    cache[cache_key] = (response_data, time.time())

    return jsonify(response_data)

# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
