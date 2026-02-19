from flask import Flask, request, jsonify
import requests
import json
import datetime

app = Flask(__name__)

# Load service registry
def load_registry():
    with open("../service-registry.json", "r") as file:
        return json.load(file)

registry = load_registry()

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "AI Agent Orchestrator",
        "status": "Running",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route("/agent/optimize-delivery", methods=["GET"])
def optimize_delivery():

    city = request.args.get("city")
    capacity = request.args.get("capacity")

    if not city or not capacity:
        return jsonify({
            "error": "Both city and capacity parameters are required"
        }), 400

    # 1️⃣ Call Weather Service
    weather_url = registry["weather_service"]["base_url"] + registry["weather_service"]["endpoint"]
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()

    # 2️⃣ Call Traffic Service
    traffic_url = (
        registry["traffic_service"]["base_url"] +
        registry["traffic_service"]["endpoint"] +
        f"?city={city}"
    )
    traffic_response = requests.get(traffic_url)
    traffic_data = traffic_response.json()

    # 3️⃣ Call Fleet Service
    fleet_url = (
        registry["fleet_service"]["base_url"] +
        registry["fleet_service"]["endpoint"] +
        f"?capacity={capacity}"
    )
    fleet_response = requests.get(fleet_url)
    fleet_data = fleet_response.json()

    # 🧠 Intelligent Decision Logic
    recommendation = "Proceed with delivery"

    if traffic_data.get("congestion_level") in ["High", "Severe"]:
        recommendation = "Delay delivery due to traffic congestion"

    if weather_data.get("condition") in ["Stormy"]:
        recommendation = "Delay delivery due to bad weather"

    if not fleet_data.get("available_vehicles"):
        recommendation = "No available vehicles for required capacity"

    return jsonify({
        "input": {
            "city": city,
            "required_capacity": capacity
        },
        "weather_data": weather_data,
        "traffic_data": traffic_data,
        "fleet_data": fleet_data,
        "final_recommendation": recommendation,
        "generated_at": datetime.datetime.now().isoformat()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
