from flask import Flask, request, jsonify
import pickle
import pandas as pd
import requests

app = Flask(__name__)

# Load trained model
model = pickle.load(open("model.pkl", "rb"))

# Weather API setup
WEATHER_API_KEY = "your_openweather_api_key"
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
    app.run(debug=True)
