import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

# Load the cleaned dataset
data = pd.read_csv("cleaned_stroke_data.csv")

# Feature selection and preprocessing
X = data[['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi']]
y = data['stroke']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train the Logistic Regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save the trained model and scaler
joblib.dump(model, "stroke_model.joblib")
joblib.dump(scaler, "scaler.joblib")
print("Model and scaler saved successfully.")
