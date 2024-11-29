import pytest
from models.database import add_patient, get_all_patients, update_patient, delete_patient

# Mock patient data
patient_data = {
    "id": 1,
    "name": "John Doe",
    "age": 45,
    "gender": "Male",
    "hypertension": 0,
    "heart_disease": 0,
    "ever_married": "Yes",
    "work_type": "Private",
    "Residence_type": "Urban",
    "avg_glucose_level": 85.6,
    "bmi": 24.5,
    "smoking_status": "Never smoked",
    "stroke": 0
}

def test_add_patient():
    assert add_patient(patient_data) == True

def test_get_all_patients():
    patients = get_all_patients()
    assert isinstance(patients, list)
    assert len(patients) >= 1

def test_update_patient():
    updated_data = patient_data.copy()
    updated_data["name"] = "Jane Doe"
    assert update_patient(1, updated_data) == True

def test_delete_patient():
    assert delete_patient(1) == True
