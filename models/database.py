from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["stroke_prediction"]
patient_collection = db["patients"]

def add_patient(patient_data):
    """
    Add a new patient record to the MongoDB collection.
    """
    try:
        patient_collection.insert_one(patient_data)
        return True
    except Exception as e:
        print(f"Error adding patient: {e}")
        return False

def get_all_patients():
    """
    Retrieve all patient records from the MongoDB collection.
    """
    try:
        patients = list(patient_collection.find())
        return patients
    except Exception as e:
        print(f"Error retrieving patients: {e}")
        return []

def update_patient(patient_id, updated_data):
    """
    Update an existing patient record in the MongoDB collection.
    """
    try:
        patient_collection.update_one({"id": patient_id}, {"$set": updated_data})
        return True
    except Exception as e:
        print(f"Error updating patient: {e}")
        return False

def delete_patient(patient_id):
    """
    Delete a patient record from the MongoDB collection.
    """
    try:
        patient_collection.delete_one({"id": patient_id})
        return True
    except Exception as e:
        print(f"Error deleting patient: {e}")
        return False
