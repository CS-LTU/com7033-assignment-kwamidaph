from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pymongo import MongoClient
import bcrypt
import joblib
import csv
from flask import Response
import matplotlib.pyplot as plt
import io
import base64
from flask import render_template

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  

# MongoDB setup
mongo_client = MongoClient("mongodb://localho.st:27017/")
mongo_db = mongo_client["stroke_prediction"]
patient_collection = mongo_db["patients"]

# SQLite setup for user authentication
def init_sqlite_db():
    """
    Initialize the SQLite database for user data.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT)''')
    conn.commit()
    conn.close()

init_sqlite_db()

# Load the trained machine learning model and scaler
model = joblib.load("stroke_model.joblib")
scaler = joblib.load("scaler.joblib")

# Route: Home
@app.route('/')
def index():
    return render_template('index.html')

# Route: User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error: {e}", 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

# Route: User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        record = cursor.fetchone()
        conn.close()

        if record and bcrypt.checkpw(password, record[0]):
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

# MongoDB CRUD Operations
from models.database import add_patient, get_all_patients, update_patient, delete_patient

# Route: Add New Patient
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient_route():
    if request.method == 'POST':
        patient_data = {
            "id": int(request.form['id']),
            "name": request.form['name'],
            "age": float(request.form['age']),
            "gender": request.form['gender'],
            "hypertension": int(request.form['hypertension']),
            "heart_disease": int(request.form['heart_disease']),
            "ever_married": request.form['ever_married'],
            "work_type": request.form['work_type'],
            "Residence_type": request.form['Residence_type'],
            "avg_glucose_level": float(request.form['avg_glucose_level']),
            "bmi": float(request.form['bmi']),
            "smoking_status": request.form['smoking_status'],
            "stroke": int(request.form['stroke'])
        }

        if add_patient(patient_data):
            flash('Patient added successfully!', 'success')
        else:
            flash('Error adding patient.', 'error')
        return redirect(url_for('view_patients'))
    return render_template('add_patient.html')

# Route: View All Patients
@app.route('/view_patients')
def view_patients():
    patients = get_all_patients()
    return render_template('view_patients.html', patients=patients)

# Route: Delete Patient
@app.route('/delete_patient/<int:patient_id>')
def delete_patient_route(patient_id):
    if delete_patient(patient_id):
        flash('Patient deleted successfully!', 'success')
    else:
        flash('Error deleting patient.', 'error')
    return redirect(url_for('view_patients'))

# Route: Update Patient
@app.route('/update_patient/<int:patient_id>', methods=['GET', 'POST'])
def update_patient_route(patient_id):
    if request.method == 'POST':
        updated_data = {
            "name": request.form['name'],
            "age": float(request.form['age']),
            "gender": request.form['gender'],
            "hypertension": int(request.form['hypertension']),
            "heart_disease": int(request.form['heart_disease']),
            "ever_married": request.form['ever_married'],
            "work_type": request.form['work_type'],
            "Residence_type": request.form['Residence_type'],
            "avg_glucose_level": float(request.form['avg_glucose_level']),
            "bmi": float(request.form['bmi']),
            "smoking_status": request.form['smoking_status'],
            "stroke": int(request.form['stroke'])
        }

        if update_patient(patient_id, updated_data):
            flash('Patient updated successfully!', 'success')
        else:
            flash('Error updating patient.', 'error')
        return redirect(url_for('view_patients'))
    return render_template('update_patient.html', patient_id=patient_id)

# Route: Stroke Prediction
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # Extract input features from the form
            age = float(request.form['age'])
            hypertension = int(request.form['hypertension'])
            heart_disease = int(request.form['heart_disease'])
            avg_glucose_level = float(request.form['avg_glucose_level'])
            bmi = float(request.form['bmi'])

            # Server-side validation
            if not (0 <= age <= 120):
                flash("Age must be between 0 and 120.", 'error')
                return render_template('predict.html', result=None)

            if hypertension not in [0, 1]:
                flash("Hypertension must be 0 or 1.", 'error')
                return render_template('predict.html', result=None)

            if heart_disease not in [0, 1]:
                flash("Heart Disease must be 0 or 1.", 'error')
                return render_template('predict.html', result=None)

            if avg_glucose_level <= 0:
                flash("Average Glucose Level must be greater than 0.", 'error')
                return render_template('predict.html', result=None)

            if bmi <= 0:
                flash("BMI must be greater than 0.", 'error')
                return render_template('predict.html', result=None)

            # Standardize the input features
            input_data = [[age, hypertension, heart_disease, avg_glucose_level, bmi]]
            input_data = scaler.transform(input_data)

            # Make the prediction
            prediction = model.predict(input_data)
            result = "Stroke" if prediction[0] == 1 else "No Stroke"
            
            # Save the prediction result to MongoDB
            prediction_data = {
                "age": age,
                "hypertension": hypertension,
                "heart_disease": heart_disease,
                "avg_glucose_level": avg_glucose_level,
                "bmi": bmi,
                "prediction": result
            }
            patient_collection.insert_one(prediction_data)
            
            flash(f"Prediction: {result}", 'success')
            return render_template('predict.html', result=result)
        except Exception as e:
            flash(f"Error: {e}", 'error')
            return render_template('predict.html', result="An error occurred.")
    return render_template('predict.html', result=None)

# Route: View Prediction History
@app.route('/view_predictions')
def view_predictions():
    try:
        predictions = list(patient_collection.find({}, {"_id": 0}))  # Exclude the MongoDB ID field
        return render_template('view_predictions.html', predictions=predictions)
    except Exception as e:
        flash(f"Error retrieving predictions: {e}", 'error')
        return redirect(url_for('index'))

# Route: Export Prediction History to CSV
@app.route('/export_predictions')
def export_predictions():
    try:
        # Fetch all predictions from MongoDB
        predictions = list(patient_collection.find({}, {"_id": 0}))

        # Define the CSV headers
        headers = ["age", "hypertension", "heart_disease", "avg_glucose_level", "bmi", "prediction"]

        # Create the CSV content
        def generate_csv():
            # Yield the headers
            yield ','.join(headers) + '\n'
            for prediction in predictions:
                row = [
                    str(prediction.get("age", "")),
                    str(prediction.get("hypertension", "")),
                    str(prediction.get("heart_disease", "")),
                    str(prediction.get("avg_glucose_level", "")),
                    str(prediction.get("bmi", "")),
                    str(prediction.get("prediction", ""))
                ]
                yield ','.join(row) + '\n'

        # Create the Flask response with CSV mimetype
        response = Response(generate_csv(), mimetype="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=prediction_history.csv"
        return response

    except Exception as e:
        flash(f"Error exporting predictions: {e}", 'error')
        return redirect(url_for('view_predictions'))
    
import matplotlib.pyplot as plt
import io
import base64
from flask import render_template

# Route: Dashboard
@app.route('/dashboard')
def dashboard():
    try:
        # Fetch all prediction data from MongoDB
        predictions = list(patient_collection.find({}, {"_id": 0}))

        # Prepare data for visualizations
        ages = [p.get("age", 0) for p in predictions]
        predictions_result = [p.get("prediction", "No Stroke") for p in predictions]
        hypertension = [p.get("hypertension", 0) for p in predictions]
        heart_disease = [p.get("heart_disease", 0) for p in predictions]

        # Create plots
        fig, axs = plt.subplots(1, 3, figsize=(18, 5))

        # Plot 1: Age Distribution
        axs[0].hist(ages, bins=20, color='skyblue', edgecolor='black')
        axs[0].set_title('Age Distribution of Patients')
        axs[0].set_xlabel('Age')
        axs[0].set_ylabel('Frequency')

        # Plot 2: Stroke Prediction Results
        stroke_count = predictions_result.count("Stroke")
        no_stroke_count = predictions_result.count("No Stroke")
        axs[1].bar(['Stroke', 'No Stroke'], [stroke_count, no_stroke_count], color=['red', 'green'])
        axs[1].set_title('Prediction Results')
        axs[1].set_xlabel('Prediction')
        axs[1].set_ylabel('Count')

        # Plot 3: Hypertension vs. Heart Disease
        hypertension_count = sum(hypertension)
        heart_disease_count = sum(heart_disease)
        axs[2].bar(['Hypertension', 'Heart Disease'], [hypertension_count, heart_disease_count], color=['orange', 'purple'])
        axs[2].set_title('Hypertension and Heart Disease Analysis')
        axs[2].set_xlabel('Condition')
        axs[2].set_ylabel('Count')

        # Save the plots to a PNG image
        img = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        return render_template('dashboard.html', plot_url=plot_url)

    except Exception as e:
        flash(f"Error generating dashboard: {e}", 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
