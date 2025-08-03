from flask import Flask, render_template, request, jsonify
import requests
import datetime
import os
import json

app = Flask(__name__)
EXPORT_DIR = "weather_exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

ICON_MAP = {
    0: '☀️ Clear',
    1: '🌤️ Mainly Clear',
    2: '⛅ Partly Cloudy',
    3: '☁️ Overcast',
    45: '🌫️ Fog',
    48: '🌫️ Depositing Fog',
    51: '🌦️ Light Drizzle',
    53: '🌦️ Moderate Drizzle',
    55: '🌧️ Dense Drizzle',
    61: '🌧️ Slight Rain',
    63: '🌧️ Moderate Rain',
    65: '🌧️ Heavy Rain',
    71: '❄️ Slight Snow',
    73: '❄️ Moderate Snow',
    75: '❄️ Heavy Snow',
    95: '⛈️ Thunderstorm'
}

def get_coordinates(city):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {'name': city, 'count': 1, 'language': 'en'}
    res = requests.get(geo_url, params=params)
    data = res.json()
    if data.get('results'):
        r = data['results'][0]
        return r['latitude'], r['longitude'], r['name'], r['country']
    else:
        raise ValueError("City not found")

def get_weather(city):
    lat, lon, name, country = get_coordinates(city)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': 'temperature_2m,weathercode',
        'timezone': 'auto'
    }
    res = requests.get(url, params=params)
    data = res.json()
    current = data['current']
    icon = ICON_MAP.get(current['weathercode'], '❓ Unknown')
    now = datetime.datetime.now()

    weather = {
        'City': f"{name}, {country}",
        'DateTime': now.strftime('%Y-%m-%d %H:%M:%S'),
        'Temperature': f"{current['temperature_2m']} °C",
        'Weather': icon
    }

    # Save as JSON & TXT
    filename_base = os.path.join(EXPORT_DIR, f"{name}_{now.strftime('%Y%m%d_%H%M%S')}")
    with open(filename_base + ".json", 'w') as f:
        json.dump(weather, f, indent=4)
    with open(filename_base + ".txt", 'w') as f:
        for k, v in weather.items():
            f.write(f"{k}: {v}\n")

    return weather

@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    error = None
    if request.method == 'POST':
        city = request.form.get('city')
        try:
            weather = get_weather(city)
        except Exception as e:
            error = str(e)
    return render_template('index.html', weather=weather, error=error)

@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {'name': query, 'count': 5, 'language': 'en'}
        response = requests.get(geo_url, params=params)
        results = response.json().get('results', [])
        suggestions = [f"{r['name']}, {r['country']}" for r in results]
        return jsonify(suggestions)
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
