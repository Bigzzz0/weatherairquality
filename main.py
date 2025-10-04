
from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import sqlite3
import datetime
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

app = Flask(__name__, template_folder='templates')

API_KEY = os.getenv("API_KEY")
GEMINI_API_KEY = "AIzaSyB5WOl4Z-hI1caON_KtyJPZuoDTQwIqAzE"

WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
AIR_QUALITY_API_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
FORECAST_API_URL = "https://api.openweathermap.org/data/2.5/forecast"

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            city TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def get_aqi_description(aqi):
    return {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}.get(aqi, "Unknown")

def get_wind_direction(deg):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = round(deg / (360. / len(directions)))
    return directions[idx % len(directions)]

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT city FROM favorites')
    favorites = [row[0] for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', favorites=favorites)

@app.route('/weather')
def get_weather():
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    params = {'appid': API_KEY, 'units': 'metric'}
    if lat and lon:
        params['lat'] = lat
        params['lon'] = lon
    elif city:
        params['q'] = city
    else:
        return jsonify({"error": "City or coordinates must be provided"}), 400

    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        tz_offset = datetime.timedelta(seconds=data['timezone'])
        tz = datetime.timezone(tz_offset)
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"], tz=tz).strftime('%-I:%M %p')
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"], tz=tz).strftime('%-I:%M %p')

        weather_data = {
            "city": data["name"],
            "temperature": round(data["main"]["temp"]),
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"] * 3.6,
            "wind_direction": get_wind_direction(data["wind"]["deg"]), 
            "wind_deg": data["wind"]["deg"], 
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"],
            "description": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
            "feels_like": round(data["main"]["feels_like"]),
            "temp_min": round(data["main"]["temp_min"]),
            "temp_max": round(data["main"]["temp_max"]),
            "sunrise": sunrise,
            "sunset": sunset
        }
        return jsonify(weather_data)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching weather data: {e}")
        return jsonify({"error": "Error fetching weather data"}), 500
    except KeyError as e:
        app.logger.error(f"Invalid data received from weather API: {e}")
        return jsonify({"error": "Invalid data received from weather API"}), 500

@app.route('/air_quality')
def get_air_quality():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        app.logger.error("AIR_QUALITY: Latitude or longitude not provided.")
        return jsonify({"error": "Latitude or longitude not provided"}), 400

    params = {'lat': lat, 'lon': lon, 'appid': API_KEY}
    app.logger.debug(f"AIR_QUALITY: Requesting API with params: {params}")
    
    try:
        response = requests.get(AIR_QUALITY_API_URL, params=params)
        app.logger.debug(f"AIR_QUALITY: API response status code: {response.status_code}")
        app.logger.debug(f"AIR_QUALITY: API response text: {response.text}")
        response.raise_for_status()
        data = response.json()

        if 'list' in data and data['list']:
            aqi_data = data['list'][0]
            air_quality_data = {
                "aqi": aqi_data.get('main', {}).get('aqi'),
                "description": get_aqi_description(aqi_data.get('main', {}).get('aqi')),
                "components": aqi_data.get('components', {})
            }
            app.logger.debug(f"AIR_QUALITY: Successfully processed data: {air_quality_data}")
            return jsonify(air_quality_data)
        else:
            app.logger.warning("AIR_QUALITY: 'list' key not in data or is empty.")
            return jsonify({"error": "Air quality data not available"}), 404
    except requests.exceptions.RequestException as e:
        app.logger.error(f"AIR_QUALITY: RequestException: {e}")
        return jsonify({"error": "Error fetching air quality data"}), 500
    except (KeyError, IndexError) as e:
        app.logger.error(f"AIR_QUALITY: Data processing error (KeyError/IndexError): {e}")
        return jsonify({"error": "Error processing air quality data"}), 500

@app.route('/forecast')
def get_forecast():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    params = {'appid': API_KEY, 'units': 'metric'}

    if lat and lon:
        params['lat'] = lat
        params['lon'] = lon
    else:
        city = request.args.get('city')
        if not city:
            return jsonify({"error": "City or coordinates must be provided"}), 400
        params['q'] = city

    try:
        response = requests.get(FORECAST_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        daily_forecasts = defaultdict(lambda: {
            'temp_min': float('inf'), 'temp_max': float('-inf'),
            'weather': defaultdict(int), 'icon': '', 'date': '',
        })

        for item in data.get('list', []):
            dt_object = datetime.datetime.fromtimestamp(item['dt'])
            date_key = dt_object.strftime('%Y-%m-%d')
            daily_forecasts[date_key]['date'] = dt_object.strftime('%a, %b %d')
            daily_forecasts[date_key]['temp_min'] = min(daily_forecasts[date_key]['temp_min'], item['main']['temp_min'])
            daily_forecasts[date_key]['temp_max'] = max(daily_forecasts[date_key]['temp_max'], item['main']['temp_max'])
            weather_main = item['weather'][0]['main']
            daily_forecasts[date_key]['weather'][weather_main] += 1
            if dt_object.hour >= 12 and dt_object.hour < 15:
                daily_forecasts[date_key]['icon'] = item['weather'][0]['icon']
        
        final_forecast = []
        sorted_keys = sorted(daily_forecasts.keys())
        for date_key in sorted_keys:
            forecast = daily_forecasts[date_key]
            if not forecast['date']: continue

            dominant_weather = max(forecast['weather'], key=forecast['weather'].get) if forecast['weather'] else 'N/A'
            if not forecast['icon']:
                for item in data.get('list', []):
                    if datetime.datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d') == date_key:
                        forecast['icon'] = item['weather'][0]['icon']
                        break
            
            final_forecast.append({
                'date': forecast['date'],
                'temp_min': round(forecast['temp_min']),
                'temp_max': round(forecast['temp_max']),
                'description': dominant_weather,
                'icon': forecast['icon'] or '01d'
            })
        
        return jsonify(final_forecast[:5])

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching forecast data: {e}")
        return jsonify({"error": "Error fetching forecast data"}), 500
    except KeyError as e:
        app.logger.error(f"Invalid data received from forecast API: {e}")
        return jsonify({"error": "Invalid data received from forecast API"}), 500

@app.route('/health_analysis', methods=['POST'])
def health_analysis():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Gemini API key not configured."}), 500

    data = request.get_json()
    weather_data = data.get('weather_data')
    air_quality_data = data.get('air_quality_data')

    if not all([weather_data, air_quality_data]):
        return jsonify({"error": "Weather and air quality data are required."}), 400

    prompt = f'''
        As a weather and air quality expert in Thailand, analyze the following data for {weather_data.get('city', 'N/A')}:
        - Weather: {weather_data.get('temperature', 'N/A')}°C (feels like {weather_data.get('feels_like', 'N/A')}°C), {weather_data.get('description', 'N/A')}, Humidity: {weather_data.get('humidity', 'N/A')}%, Wind: {weather_data.get('wind_speed', 0):.1f} km/h.
        - Air Quality: AQI is {air_quality_data.get('aqi', 'N/A')} ({air_quality_data.get('description', 'N/A')}). Pollutants (μg/m³): PM2.5: {air_quality_data.get('components', {}).get('pm2_5', 'N/A')}, PM10: {air_quality_data.get('components', {}).get('pm10', 'N/A')}, O3: {air_quality_data.get('components', {}).get('o3', 'N/A')}.
        Provide health and activity recommendations in Thai. Start with a 1-2 sentence summary, followed by a bulleted list of actionable advice.
    '''
    
    gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(gemini_api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        app.logger.debug(f"Gemini API Response: {response.json()}")

        candidates = response.json().get('candidates', [])
        if not candidates:
            raise ValueError("No candidates found in Gemini response")
        
        content_parts = candidates[0].get('content', {}).get('parts', [])
        if not content_parts:
            raise ValueError("No parts found in Gemini response content")

        analysis_text = content_parts[0].get('text', '')
        if not analysis_text:
             raise ValueError("Empty text returned from Gemini")

        return jsonify({"analysis": analysis_text})

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling Gemini REST API: {e}")
        if e.response is not None:
            app.logger.error(f"Gemini API Error Response: {e.response.text}")
        return jsonify({"error": "Failed to get AI analysis"}), 500
    except (ValueError, KeyError, IndexError) as e:
        app.logger.error(f"Error parsing Gemini API response: {e}")
        return jsonify({"error": "Failed to parse AI analysis"}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred in health_analysis: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/favorites', methods=['GET', 'POST', 'DELETE'])
def handle_favorites():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if request.method == 'GET':
        cursor.execute('SELECT city FROM favorites')
        favorites = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify(favorites)

    data = request.get_json()
    city = data.get('city')
    if not city:
        conn.close()
        return jsonify({"error": "City not provided"}), 400

    if request.method == 'POST':
        try:
            cursor.execute('INSERT INTO favorites (city) VALUES (?)', (city,))
            conn.commit()
            message = {"success": True, "city": city}
        except sqlite3.IntegrityError:
            message = {"error": "City already in favorites"}
    
    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM favorites WHERE city = ?', (city,))
        conn.commit()
        message = {"success": True, "city": city}

    conn.close()
    return jsonify(message)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8080)