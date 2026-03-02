from middleware.request_id import attach_request_id
from utils.logger import setup_logger
from config.settings import Settings
from flask import Flask, request, jsonify, render_template
import requests
import json
import uuid
import datetime
import time
import uuid
import os
import logging
from dotenv import load_dotenv

# =========================================================
# INITIALIZATION
# =========================================================

load_dotenv()

app = Flask(__name__)

API_KEY = Settings.API_KEY
CACHE_TTL = Settings.CACHE_TTL

SERVICE_REGISTRY_PATH = "../service-registry.json"

FAILURE_THRESHOLD = 3
COOLDOWN_TIME = 30
RATE_LIMIT = 20
RATE_WINDOW = 60

# =========================================================
# GLOBAL STATE
# =========================================================

cache = {}
request_counts = {}

metrics = {
    "total_requests": 0,
    "cache_hits": 0,
    "agent_executions": 0,
    "average_latency": 0,
    "uptime_start": time.time()
}

circuit_breakers = {
    "weather": {"failures": 0, "state": "CLOSED", "last_failure_time": None},
    "traffic": {"failures": 0, "state": "CLOSED", "last_failure_time": None},
    "fleet": {"failures": 0, "state": "CLOSED", "last_failure_time": None},
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# =========================================================
# LOAD SERVICE REGISTRY
# =========================================================

def load_registry():
    with open(SERVICE_REGISTRY_PATH, "r") as file:
        return json.load(file)

registry = load_registry()

# =========================================================
# AUTHENTICATION
# =========================================================

def authenticate(req):
    return req.headers.get("x-api-key") == API_KEY

# =========================================================
# RATE LIMITING
# =========================================================

def check_rate_limit():
    client_ip = request.remote_addr
    current_time = time.time()

    if client_ip not in request_counts:
        request_counts[client_ip] = []

    request_counts[client_ip] = [
        t for t in request_counts[client_ip]
        if current_time - t < RATE_WINDOW
    ]

    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return False

    request_counts[client_ip].append(current_time)
    return True

# =========================================================
# CIRCUIT BREAKER SERVICE CALL
# =========================================================

def safe_call_service(service_name, url, retries=2, timeout=3):
    breaker = circuit_breakers[service_name]

    if breaker["state"] == "OPEN":
        if time.time() - breaker["last_failure_time"] < COOLDOWN_TIME:
            return {"error": "Service temporarily unavailable (circuit open)"}
        else:
            breaker["state"] = "CLOSED"
            breaker["failures"] = 0

    for _ in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            breaker["failures"] = 0
            return response.json()
        except Exception:
            pass

    breaker["failures"] += 1
    breaker["last_failure_time"] = time.time()

    if breaker["failures"] >= FAILURE_THRESHOLD:
        breaker["state"] = "OPEN"

    return {"error": "Service unavailable"}

# =========================================================
# INTELLIGENT DECISION ENGINE
# =========================================================

def intelligent_decision(weather, traffic, fleet):
    explanation = []
    decision = "Proceed with delivery"

    if traffic.get("congestion_level") in ["High", "Severe"]:
        decision = "Delay delivery"
        explanation.append("High traffic congestion detected.")

    if weather.get("condition") in ["Stormy", "Heavy Rain"]:
        decision = "Delay delivery"
        explanation.append("Adverse weather conditions.")

    if not fleet.get("available_vehicles"):
        decision = "Delivery not possible"
        explanation.append("No available vehicles with required capacity.")

    if not explanation:
        explanation.append("All operational parameters are within normal range.")

    return {
        "decision": decision,
        "explanation": explanation
    }

# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def home():
    return jsonify({
        "service": "Intelligent API Agent Gateway",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "circuit_breakers": circuit_breakers
    })

@app.route("/metrics")
def get_metrics():
    uptime = round(time.time() - metrics["uptime_start"], 2)
    return jsonify({
        **metrics,
        "uptime_seconds": uptime
    })

@app.route("/docs")
def docs():
    return jsonify({
        "endpoint": "/agent/optimize-delivery",
        "method": "GET",
        "headers_required": ["x-api-key"],
        "query_params": {
            "city": "string",
            "capacity": "integer"
        }
    })

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# =========================================================
# MAIN AGENT ENDPOINT
# =========================================================

@app.route("/agent/optimize-delivery")
def optimize_delivery():

    request_id = str(uuid.uuid4())
    start_time = time.time()

    metrics["total_requests"] += 1

    if not authenticate(request):
        return jsonify({"error": "Unauthorized"}), 401

    if not check_rate_limit():
        return jsonify({"error": "Rate limit exceeded"}), 429

    city = request.args.get("city")
    capacity = request.args.get("capacity")

    if not city or not capacity:
        return jsonify({"error": "city and capacity required"}), 400

    cache_key = f"{city}-{capacity}"

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

    latency = round(time.time() - start_time, 3)
    metrics["average_latency"] = latency

    response_data = {
        "request_id": request_id,
        "input": {"city": city, "capacity": capacity},
        "weather": weather_data,
        "traffic": traffic_data,
        "fleet": fleet_data,
        "agent_decision": decision_result,
        "processing_time_seconds": latency,
        "generated_at": datetime.datetime.utcnow().isoformat()
    }

    cache[cache_key] = (response_data, time.time())

    return jsonify(response_data)

# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)