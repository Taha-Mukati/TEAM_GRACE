import streamlit as st
import requests

#get the host
import os
host = "127.0.0.1"
try:
    host = os.environ['DockHost']
except:
    host = "127.0.0.1"

st.title("🚦 Real-Time Accident Risk Predictor")
st.write("Enter a location and time to get an accident risk score.")

location = st.text_input("Enter location (City, Country):")
hour = st.slider("Select Hour of the Day", 0, 23, 12)

if st.button("Predict Risk"):
    response = requests.get(f"http://{host}:5000/predict?location={location}&hour={hour}")
    if response.status_code == 200:
        result = response.json()
        st.success(f"Predicted Risk Score: {result['risk_score']}%")
        st.write(f"Severity Level: {result['severity']}")
    else:
        st.error("Error fetching prediction")
