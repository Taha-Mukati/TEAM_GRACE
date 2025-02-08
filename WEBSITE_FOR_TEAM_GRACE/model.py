import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
df = pd.read_csv("traffic_accidents.csv")

# Select features
features = ["crash_hour", "crash_day_of_week", "weather_condition", "roadway_surface_cond"]
df = df.dropna(subset=features)

# Convert categorical variables
df = pd.get_dummies(df, columns=["weather_condition", "roadway_surface_cond"])

X = df[["crash_hour", "crash_day_of_week"] + [col for col in df.columns if "weather_condition_" in col or "roadway_surface_cond_" in col]]
y = (df["injuries_total"] > 0).astype(int)  # 1 = High risk, 0 = Low risk

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

pickle.dump(model, open("model.pkl", "wb"))
