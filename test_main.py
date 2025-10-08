import pytest
from main import app, get_aqi_description, get_wind_direction
import json
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


def test_get_aqi_description_mapping():
    assert get_aqi_description(1) == "Good"
    assert get_aqi_description(3) == "Moderate"
    assert get_aqi_description(5) == "Very Poor"
    # Unknown values should return "Unknown"
    assert get_aqi_description(99) == "Unknown"


def test_get_wind_direction_boundaries():
    assert get_wind_direction(0) == "N"
    assert get_wind_direction(45) == "NE"
    assert get_wind_direction(90) == "E"
    assert get_wind_direction(225) == "SW"


def test_forecast_processing(monkeypatch, client):
    sample_data = {
        "list": [
            {
                "dt": 1704110400,  # 2024-01-01 12:00 UTC
                "main": {"temp_min": 20.4, "temp_max": 25.6},
                "weather": [{"main": "Clear", "icon": "01d"}]
            },
            {
                "dt": 1704121200,  # 2024-01-01 15:00 UTC
                "main": {"temp_min": 18.0, "temp_max": 27.3},
                "weather": [{"main": "Clouds", "icon": "02d"}]
            },
            {
                "dt": 1704196800,  # 2024-01-02 12:00 UTC
                "main": {"temp_min": 22.1, "temp_max": 28.9},
                "weather": [{"main": "Rain", "icon": "09d"}]
            },
            {
                "dt": 1704207600,  # 2024-01-02 15:00 UTC
                "main": {"temp_min": 21.5, "temp_max": 29.2},
                "weather": [{"main": "Rain", "icon": "10d"}]
            },
        ]
    }

    class DummyResponse:
        status_code = 200
        text = json.dumps(sample_data)

        def raise_for_status(self):
            return None

        def json(self):
            return sample_data

    def dummy_get(url, params=None, **kwargs):
        return DummyResponse()

    monkeypatch.setattr('main.API_KEY', 'test-key')
    monkeypatch.setattr('main.requests.get', dummy_get)

    response = client.get('/forecast?city=Bangkok')
    assert response.status_code == 200
    assert response.is_json
    forecast = response.get_json()
    assert isinstance(forecast, list)
    assert len(forecast) == 2

    first_day = forecast[0]
    assert first_day["date"] == "Mon, Jan 01"
    assert first_day["temp_min"] == 18
    assert first_day["temp_max"] == 27
    assert first_day["description"] == "Clear"
    assert first_day["icon"] == "01d"

    second_day = forecast[1]
    assert second_day["date"] == "Tue, Jan 02"
    assert second_day["temp_min"] == 22
    assert second_day["temp_max"] == 29
    assert second_day["description"] == "Rain"
    assert second_day["icon"] == "09d"


def test_health_analysis_missing_payload(client):
    response = client.post('/health_analysis', json={})
    assert response.status_code == 400
    assert response.is_json
    assert "error" in response.get_json()

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__]))