
from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import sqlite3
import datetime
from collections import defaultdict
import google.generativeai as genai

load_dotenv()

app = Flask(__name__, template_folder='templates')

API_KEY = os.getenv("API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Google Generative AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro') # Using gemini-pro model
else:
    gemini_model = None
    print("WARNING: GEMINI_API_KEY not found in .env. AI analysis will be unavailable.")

WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
AIR_QUALITY_API_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
FORECAST_API_URL = "http://api.openweathermap.org/data/2.5/forecast"

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
    if aqi == 1: return "Good"
    if aqi == 2: return "Fair"
    if aqi == 3: return "Moderate"
    if aqi == 4: return "Poor"
    if aqi == 5: return "Very Poor"
    return "Very Poor"

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

        # Convert sunrise/sunset times
        tz_offset = datetime.timedelta(seconds=data['timezone'])
        tz = datetime.timezone(tz_offset)
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"], tz=tz).strftime('%-I:%M %p')
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"], tz=tz).strftime('%-I:%M %p')

        weather_data = {
            "city": data["name"],
            "temperature": round(data["main"]["temp"]),
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"] * 3.6, # Convert m/s to km/h
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
        return jsonify({"error": f"Error fetching weather data: {e}"}), 500
    except KeyError:
        return jsonify({"error": "Invalid data received from weather API"}), 500

@app.route('/air_quality')
def get_air_quality():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        print("AIR_QUALITY_DEBUG: Latitude or longitude not provided.")
        return jsonify({"error": "Latitude or longitude not provided"}), 400

    params = {'lat': lat, 'lon': lon, 'appid': API_KEY}
    log_params = params.copy()
    if log_params.get('appid'):
        log_params['appid'] = f"{log_params['appid'][:4]}..."
    print(f"AIR_QUALITY_DEBUG: Requesting Air Quality API with params: {log_params}")
    
    try:
        response = requests.get(AIR_QUALITY_API_URL, params=params)
        print(f"AIR_QUALITY_DEBUG: API response status code: {response.status_code}")
        print(f"AIR_QUALITY_DEBUG: API response text: {response.text}")
        response.raise_for_status()
        data = response.json()

        if 'list' in data and data['list']:
            aqi_data = data['list'][0]
            air_quality_data = {
                "aqi": aqi_data['main']['aqi'],
                "description": get_aqi_description(aqi_data['main']['aqi']),
                "components": aqi_data['components']
            }
            print(f"AIR_QUALITY_DEBUG: Successfully processed data: {air_quality_data}")
            return jsonify(air_quality_data)
        else:
            print("AIR_QUALITY_DEBUG: 'list' key not in data or is empty.")
            return jsonify({"error": "Air quality data not available"}), 404
    except requests.exceptions.RequestException as e:
        print(f"AIR_QUALITY_DEBUG: RequestException: {e}")
        return jsonify({"error": f"Error fetching air quality data: {e}"}), 500
    except (KeyError, IndexError) as e:
        print(f"AIR_QUALITY_DEBUG: Data processing error (KeyError/IndexError): {e}")
        return jsonify({"error": f"Error processing air quality data: {e}"}), 500

@app.route('/forecast')
def get_forecast():
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
        response = requests.get(FORECAST_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        daily_forecasts = defaultdict(lambda: {
            'temp_min': float('inf'),
            'temp_max': float('-inf'),
            'weather': defaultdict(int),
            'icon': '',
            'date': '',
        })

        for item in data['list']:
            dt_object = datetime.datetime.fromtimestamp(item['dt'])
            date_key = dt_object.strftime('%Y-%m-%d')
            daily_forecasts[date_key]['date'] = dt_object.strftime('%a, %b %d')

            temp = item['main']['temp']
            daily_forecasts[date_key]['temp_min'] = min(daily_forecasts[date_key]['temp_min'], temp)
            daily_forecasts[date_key]['temp_max'] = max(daily_forecasts[date_key]['temp_max'], temp)
            
            weather_main = item['weather'][0]['main']
            daily_forecasts[date_key]['weather'][weather_main] += 1
            # For simplicity, just take the icon from the midday forecast
            if dt_object.hour >= 12 and dt_object.hour < 15 and not daily_forecasts[date_key]['icon']:
                daily_forecasts[date_key]['icon'] = item['weather'][0]['icon']

        # Convert defaultdict to a regular dict and select dominant weather
        final_forecast = []
        for date_key in sorted(daily_forecasts.keys()):
            forecast = daily_forecasts[date_key]
            if forecast['date']:
                dominant_weather = max(forecast['weather'], key=forecast['weather'].get) if forecast['weather'] else 'Unknown'
                
                # If icon is not set (e.g., no midday forecast), pick one from the day
                if not forecast['icon'] and forecast['weather']:
                    # Find an icon for the dominant weather
                    for item in data['list']:
                        dt_object = datetime.datetime.fromtimestamp(item['dt'])
                        if dt_object.strftime('%Y-%m-%d') == date_key and item['weather'][0]['main'] == dominant_weather:
                            forecast['icon'] = item['weather'][0]['icon']
                            break
                    
                final_forecast.append({
                    'date': forecast['date'],
                    'temp_min': round(forecast['temp_min']),
                    'temp_max': round(forecast['temp_max']),
                    'description': dominant_weather,
                    'icon': forecast['icon'] if forecast['icon'] else '01d' # Fallback icon
                })
        
        # Limit to 5 days, excluding the current day if the first entry is today's partial forecast
        # OpenWeatherMap forecast usually includes the current day's remaining 3-hour slots
        # We want next 5 *full* days. Simplistically, we'll take 5 entries if available.
        return jsonify(final_forecast[1:6] if len(final_forecast) > 5 else final_forecast)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error fetching forecast data: {e}"}), 500
    except KeyError as e:
        return jsonify({"error": f"Invalid data received from forecast API: {e}"}), 500

# New endpoint to get AI-powered health recommendations
@app.route('/health_analysis', methods=['POST'])
def health_analysis():
    if not gemini_model:
        return jsonify({"error": "Gemini API key not configured."}), 500

    data = request.get_json()
    weather_data = data.get('weather_data')
    air_quality_data = data.get('air_quality_data')
    wind_speed = data.get('wind_speed')

    if not weather_data or not air_quality_data or wind_speed is None:
        return jsonify({"error": "All required data (weather, air quality, wind speed) are needed for analysis."}), 400

    prompt = f'''
        คุณคือผู้เชี่ยวชาญด้านสภาพอากาศและคุณภาพอากาศในประเทศไทย ช่วยวิเคราะห์ข้อมูลต่อไปนี้:

        สภาพอากาศปัจจุบันสำหรับ {weather_data['city']}:
        อุณหภูมิ: {weather_data['temperature']}°C (รู้สึกเหมือน {weather_data['feels_like']}°C)
        สภาพ: {weather_data['description']}
        ความชื้น: {weather_data['humidity']}%
        ความเร็วลม: {wind_speed:.1f} km/h จากทิศ {weather_data['wind_direction']}
        พระอาทิตย์ขึ้น: {weather_data['sunrise']}, พระอาทิตย์ตก: {weather_data['sunset']}

        คุณภาพอากาศ (AQI) สำหรับ {weather_data['city']}:
        AQI: {air_quality_data['aqi']} ({air_quality_data['description']})
        ส่วนประกอบมลพิษ (μg/m³):
        CO: {air_quality_data['components'].get('co', 0):.2f}
        NO: {air_quality_data['components'].get('no', 0):.2f}
        NO2: {air_quality_data['components'].get('no2', 0):.2f}
        O3: {air_quality_data['components'].get('o3', 0):.2f}
        SO2: {air_quality_data['components'].get('so2', 0):.2f}
        PM2.5: {air_quality_data['components'].get('pm2_5', 0):.2f}
        PM10: {air_quality_data['components'].get('pm10', 0):.2f}

        โปรดให้คำแนะนำที่เป็นประโยชน์ต่อสุขภาพและการวางแผนกิจกรรมต่างๆ เช่น การเดินทาง การออกกำลังกาย หรือกิจกรรมกลางแจ้งอื่นๆ โดยเน้นการสื่อสารที่เป็นมิตรและเข้าใจง่ายในภาษาไทย. หากมีข้อมูลที่สำคัญหรือน่าเป็นห่วง โปรดเน้นย้ำและให้คำแนะนำที่ชัดเจนและเป็นไปได้จริง. กรุณาเริ่มต้นด้วยข้อความสรุปการวิเคราะห์สั้นๆ หนึ่งถึงสองประโยค แล้วตามด้วยคำแนะนำเป็นข้อๆ (list format).
        '''
    try:
        response = gemini_model.generate_content(prompt)
        ai_analysis = response.text
        return jsonify({"analysis": ai_analysis})
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return jsonify({"error": f"Failed to get AI analysis: {e}"}), 500

@app.route('/favorites', methods=['GET'])
def get_favorites():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT city FROM favorites')
    favorites = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(favorites)

@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.get_json()
    city = data.get('city')
    if not city: return jsonify({"error": "City not provided"}), 400
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO favorites (city) VALUES (?)', (city,))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "City already in favorites"}), 400
    finally:
        conn.close()
    return jsonify({"success": True, "city": city})

@app.route('/favorites', methods=['DELETE'])
def remove_favorite():
    data = request.get_json()
    city = data.get('city')
    if not city: return jsonify({"error": "City not provided"}), 400
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM favorites WHERE city = ?', (city,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "city": city})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
