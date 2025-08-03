import tkinter as tk
from tkinter import messagebox
import requests
import datetime
import json
import os

# --- CONFIG ---
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
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

# --- FUNCTIONS ---
def get_coordinates(city):
    params = {'name': city, 'count': 1, 'language': 'en', 'format': 'json'}
    res = requests.get(GEOCODE_API_URL, params=params)
    data = res.json()
    if data.get('results'):
        result = data['results'][0]
        return result['latitude'], result['longitude'], result['name'], result['country']
    else:
        raise ValueError("City not found")

def get_weather(city):
    lat, lon, city_name, country = get_coordinates(city)
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': 'temperature_2m,weathercode',
        'timezone': 'auto'
    }
    res = requests.get(WEATHER_API_URL, params=params)
    data = res.json()
    current = data['current']
    weather_code = current['weathercode']
    icon = ICON_MAP.get(weather_code, '❓ Unknown')
    now = datetime.datetime.now()

    weather = {
        'City': f"{city_name}, {country}",
        'Date & Time': now.strftime('%Y-%m-%d %H:%M:%S'),
        'Temperature': f"{current['temperature_2m']} °C",
        'Weather': icon
    }
    return weather

def show_weather():
    city = city_entry.get()
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return
    try:
        weather = get_weather(city)
        display = "\n".join([f"{k}: {v}" for k, v in weather.items()])
        result_label.config(text=display)
        export_weather_data(weather)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def export_weather_data(data):
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    txt_file = os.path.join(EXPORT_DIR, f"{data['City'].replace(', ', '_')}_{now}.txt")
    json_file = os.path.join(EXPORT_DIR, f"{data['City'].replace(', ', '_')}_{now}.json")

    with open(txt_file, 'w') as f:
        for k, v in data.items():
            f.write(f"{k}: {v}\n")

    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

# --- GUI SETUP ---
root = tk.Tk()
root.title("🌤️ Open-Meteo Weather Dashboard")
root.geometry("400x400")
root.configure(bg="#1e1e1e")
root.resizable(False, False)

style = {"font": ("Segoe UI", 12), "bg": "#1e1e1e", "fg": "#ffffff"}

tk.Label(root, text="Enter City:", **style).pack(pady=(20, 5))
city_entry = tk.Entry(root, font=("Segoe UI", 12), width=25, bg="#2e2e2e", fg="white", insertbackground="white")
city_entry.pack(pady=5)

tk.Button(root, text="Get Weather", font=("Segoe UI", 12), bg="#444", fg="white", command=show_weather).pack(pady=10)

result_label = tk.Label(root, font=("Consolas", 11), justify="left", bg="#1e1e1e", fg="lightgreen")
result_label.pack(pady=20)

tk.Label(root, text="Powered by Open-Meteo • Free API", font=("Arial", 9), bg="#1e1e1e", fg="#888").pack(side="bottom", pady=10)

root.mainloop()
