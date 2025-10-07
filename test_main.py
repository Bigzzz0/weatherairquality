import pytest
from main import app
import sys

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<html' in response.data or b'<!DOCTYPE html' in response.data

def test_weather_no_params(client):
    response = client.get('/weather')
    assert response.status_code == 400
    assert response.is_json
    assert "error" in response.get_json()

def test_air_quality_missing_params(client):
    response = client.get('/air_quality')
    assert response.status_code == 400
    assert response.is_json
    assert "error" in response.get_json()

def test_forecast_no_params(client):
    response = client.get('/forecast')
    assert response.status_code == 400
    assert response.is_json
    assert "error" in response.get_json()

def test_favorites_get(client):
    response = client.get('/favorites')
    assert response.status_code == 200
    assert response.is_json
    assert isinstance(response.get_json(), list)

def test_weather_api_key_valid(client):
    response = client.get('/weather?city=Bangkok')
    # If API key is valid, should not get 401
    assert response.status_code != 401
    # If API key is invalid, error message should be present
    if response.status_code == 200:
        assert "city" in response.get_json()
    else:
        assert "error" in response.get_json()

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__]))
