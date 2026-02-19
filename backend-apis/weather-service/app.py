from flask import Flask, jsonify
import random
import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Weather Service",
        "status": "Running",
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route("/weather", methods=["GET"])
def get_weather():
    weather_data = {
        "city": "Colombo",
        "temperature_celsius": random.randint(25, 35),
        "condition": random.choice(["Sunny", "Rainy", "Cloudy", "Stormy"]),
        "humidity_percentage": random.randint(60, 95),
        "wind_speed_kmh": random.randint(5, 30),
        "generated_at": datetime.datetime.now().isoformat()
    }

    return jsonify(weather_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
