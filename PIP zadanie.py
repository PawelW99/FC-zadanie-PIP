import requests
import json
import os
from datetime import datetime, timedelta

file_name = "weather_cache.json"
latitude = 52.23
longitude = 21.01


def get_date_input():
    user_input = input("Podaj datę (YYYY-mm-dd). Wciśnij Enter, aby wybrać jutro: ")

    if not user_input:
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%d")
    return user_input


def check_cache(date):
    if not os.path.exists(file_name):
        return None

    with open(file_name, 'r') as file:
        try:
            data = json.load(file)
            return data.get(date)
        except json.JSONDecodeError:
            return None


def save_to_cache(date, result):
    data = {}
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

    data[date] = result

    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)


def get_weather_from_api(date):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=rain&daily=rain_sum&timezone=Europe%2FLondon&start_date={date}&end_date={date}"

    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        try:
            rain_sum = json_data['daily']['rain_sum'][0]
            return rain_sum
        except (KeyError, IndexError, TypeError):
            return -1.0
    else:
        return -1.0

searched_date = get_date_input()
print(f"Sprawdzam pogodę dla daty: {searched_date}")

cached_result = check_cache(searched_date)

if cached_result:
    print(f"Wynik z pliku: {cached_result}")
else:
    print("Brak w pliku. Pobieram z API...")
    rain_amount = get_weather_from_api(searched_date)

    if rain_amount is None or rain_amount < 0:
        weather_info = "Nie wiem"
    elif rain_amount > 0.0:
        weather_info = "Będzie padać"
    else:
        weather_info = "Nie będzie padać"

    print(f"Wynik z API: {weather_info}")

    save_to_cache(searched_date, weather_info)