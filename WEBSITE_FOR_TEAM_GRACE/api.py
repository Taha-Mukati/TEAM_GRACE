from flask import Flask, request, jsonify
import pickle
import pandas as pd
import requests

app = Flask(__name__)

weather_mapping = {
    "Thunderstorm": "RAIN",
    "Drizzle": "RAIN",
    "Rain": "RAIN",
    "Snow": "SNOW",
    "Mist": "FOG/SMOKE/HAZE",
    "Smoke": "FOG/SMOKE/HAZE",
    "Haze": "FOG/SMOKE/HAZE",
    "Dust": "BLOWING SAND, SOIL, DIRT",
    "Fog": "FOG/SMOKE/HAZE",
    "Sand": "BLOWING SAND, SOIL, DIRT",
    "Ash": "OTHER",
    "Squall": "SEVERE CROSS WIND GATE",
    "Tornado": "OTHER",
    "Clear": "CLEAR",
    "Clouds": "CLOUDY/OVERCAST",
}

# Load trained model
model = pickle.load(open("model.pkl", "rb"))

# Load the saved label encoder
label_encoder = pickle.load(open("label_encoders.pkl", "rb"))
weather_encoder = label_encoders["weather_condition"]
roadway_encoder = label_encoders["roadway_surface_cond"]


# Weather API setup
WEATHER_API_KEY = "e4c2644ba4ab70ef42df5616a34e0fb7"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

@app.route("/predict", methods=["GET"])
def predict():
    location = request.args.get("location")
    hour = int(request.args.get("hour"))

    # Fetch live weather
    weather_response = requests.get(f"{WEATHER_URL}?q={location}&appid={WEATHER_API_KEY}")
    if weather_response.status_code != 200:
        return jsonify({"error": "Invalid location"}), 400

    weather_data = weather_response.json()
    weather_condition = weather_data["weather"][0]["main"]
    
    #map weather from API to weather for model
    if weather_condition in weather_mapping:
        weather_condition = weather_mapping[weather_condition]
    else:
        weather_condition = "CLEAR"
    #transform label to used data
    weather_condition = weather_encoder.transform([weather_condition])[0]
        
    # Prepare input data
    input_data = pd.DataFrame([[hour, 3, weather_condition]], columns=["crash_hour", "crash_day_of_week", "weather_condition"])
    input_data = pd.get_dummies(input_data)

    # Ensure all features exist
    for col in model.feature_names_in_:
        if col not in input_data:
            input_data[col] = 0

    # Predict risk
    risk_score = model.predict_proba(input_data)[0][1] * 100
    severity = "High" if risk_score > 70 else "Medium" if risk_score > 40 else "Low"

    return jsonify({"risk_score": round(risk_score, 2), "severity": severity})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=6000)
