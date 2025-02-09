import streamlit as st
import requests
import time

st.set_page_config(page_title="Accident Risk Predictor", layout="centered")
st.title("🚦 Real-Time Accident Risk Predictor")
st.write("Enter location, time, and road conditions to assess accident risk.")

# User inputs
location = st.text_input("Enter location (City, Country):")
hour = st.slider("Select Hour of the Day", 0, 23, 12)
day_of_week = st.selectbox("Select Day of the Week", 
                           ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], 
                           index=2)
road_condition = st.selectbox("Select Road Condition", ["Dry", "Wet", "Icy", "Snowy", "Foggy"], index=0)
lighting_condition = st.selectbox("Select Lighting Condition", ["Daylight", "Darkness", "Dawn", "Dusk"], index=0)
traffic_control = st.selectbox("Select Traffic Control Device", ["None", "Traffic Signal", "Stop Sign", "Yield Sign"], index=0)

# Convert day_of_week to numeric format
day_mapping = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
day_of_week_numeric = day_mapping[day_of_week]

if st.button("Predict Risk"):
    with st.spinner("Fetching prediction..."):
        time.sleep(1)  # Simulate loading time
        response = requests.get(f"http://127.0.0.1:5000/predict?location={location}&hour={hour}&day_of_week={day_of_week_numeric}&road_condition={road_condition}&lighting_condition={lighting_condition}&traffic_control={traffic_control}")
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"Predicted Risk Score: {result['risk_score']}%")
            st.write(f"Severity Level: {result['severity']}")
            st.write(f"Weather: {result['weather']}")
            st.write(f"Road Condition: {result['road_condition']}")
            st.write(f"Lighting Condition: {result['lighting_condition']}")
            st.write(f"Traffic Control: {result['traffic_control']}")
        else:
            st.error("Error fetching prediction. Please check your input.")