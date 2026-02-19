from flask import Flask, jsonify, request
import random
import datetime
import logging

app = Flask(__name__)

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Traffic Service",
        "status": "Running",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route("/traffic", methods=["GET"])
def get_traffic():
    city = request.args.get("city")

    if not city:
        logging.warning("City parameter missing in request")
        return jsonify({
            "error": "City parameter is required"
        }), 400

    traffic_data = {
        "city": city,
        "congestion_level": random.choice(["Low", "Moderate", "High", "Severe"]),
        "average_speed_kmh": random.randint(10, 60),
        "accident_reports": random.randint(0, 5),
        "road_closures": random.randint(0, 3),
        "generated_at": datetime.datetime.now().isoformat()
    }

    logging.info(f"Traffic data generated for city: {city}")

    return jsonify(traffic_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
