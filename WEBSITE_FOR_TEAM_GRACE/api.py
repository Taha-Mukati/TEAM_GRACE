from flask import Flask, request, jsonify
import pickle
import pandas as pd
import requests
import os
from flask_cors import CORS
from functools import lru_cache

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Load updated model
model = pickle.load(open("model.pkl", "rb"))

# Secure Weather API setup
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "your_openweather_api_key")
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

@lru_cache(maxsize=50)  # Cache weather responses to reduce API calls
def get_weather(location):
    response = requests.get(f"{WEATHER_URL}?q={location}&appid={WEATHER_API_KEY}&units=metric")
    if response.status_code == 200:
        return response.json()
    return None

@app.route("/predict", methods=["GET"])
def predict():
    location = request.args.get("location")
    hour = request.args.get("hour")
    day_of_week = request.args.get("day_of_week")
    road_condition = request.args.get("road_condition", "dry")
    lighting_condition = request.args.get("lighting_condition", "daylight")
    traffic_control = request.args.get("traffic_control", "none")
    
    if not location or not hour or not day_of_week:
        return jsonify({"error": "Missing required parameters"}), 400
    
    hour = int(hour)
    day_of_week = int(day_of_week)
    
    weather_data = get_weather(location)
    if not weather_data:
        return jsonify({"error": "Invalid location or API error"}), 400
    
    weather_condition = weather_data["weather"][0]["main"].strip().lower().replace(" ", "_")
    road_condition = road_condition.strip().lower().replace(" ", "_")
    lighting_condition = lighting_condition.strip().lower().replace(" ", "_")
    traffic_control = traffic_control.strip().lower().replace(" ", "_")

    input_data = pd.DataFrame([[hour, day_of_week, weather_condition, road_condition, lighting_condition, traffic_control]],
                              columns=["crash_hour", "crash_day_of_week", "weather_condition", "roadway_surface_cond", "lighting_condition", "traffic_control_device"])
    input_data = pd.get_dummies(input_data)

    for col in model.feature_names_in_:
        if col not in input_data:
            input_data[col] = 0

    risk_score = model.predict_proba(input_data)[0][1] * 100
    severity = "High" if risk_score > 70 else "Medium" if risk_score > 40 else "Low"

    return jsonify({
        "risk_score": round(risk_score, 2),
        "severity": severity,
        "weather": weather_condition,
        "road_condition": road_condition,
        "lighting_condition": lighting_condition,
        "traffic_control": traffic_control
    })

if __name__ == "__main__":
    app.run(debug=True)
