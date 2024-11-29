import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_predict_route(client):
    response = client.post('/predict', data={
        'age': 45,
        'hypertension': 0,
        'heart_disease': 0,
        'avg_glucose_level': 100.0,
        'bmi': 25.0
    })
    assert response.status_code == 200
    assert b"Prediction" in response.data
