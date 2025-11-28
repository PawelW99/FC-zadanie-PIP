import requests
import json
import os
from datetime import datetime, timedelta

FILE_NAME = "weather_cache.json"
LATITUDE = 52.23
LONGITUDE = 21.01


class WeatherForecast:

    def __init__(self):
        self.file_name = FILE_NAME
        self.latitude = LATITUDE
        self.longitude = LONGITUDE
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_cache(self):
        with open(self.file_name, 'w') as file:
            json.dump(self.cache, file, indent=4)

    def _get_api_result(self, date):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={self.latitude}&longitude={self.longitude}&hourly=rain&daily=rain_sum&timezone=Europe%2FLondon&start_date={date}&end_date={date}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            rain_sum = json_data['daily']['rain_sum'][0]
            return rain_sum

        except (requests.exceptions.RequestException, KeyError, IndexError, TypeError):
            return -1.0


    def __getitem__(self, date: str) -> str:
        """Pobieranie: forecast[date]"""
        if date in self.cache:
            print(f"-> Wynik dla {date} z pliku.")
            return self.cache[date]

        print(f"-> Pobieram z API dla daty: {date}")

        rain_amount = self._get_api_result(date)

        if rain_amount is None or rain_amount < 0:
            weather_info = "Nie wiem"
        elif rain_amount > 0.0:
            weather_info = "Będzie padać"
        else:
            weather_info = "Nie będzie padać"

        self.__setitem__(date, weather_info)

        return weather_info

    def __setitem__(self, date: str, weather_info: str):
        """Zapis: forecast[date] = info"""
        self.cache[date] = weather_info
        self._save_cache()

    def __iter__(self):
        """Iterowanie po kluczach: for date in forecast: ..."""
        yield from self.cache.keys()

    def items(self):
        """Generator par (data, pogoda)"""
        for date, weather in self.cache.items():
            yield (date, weather)



def get_date_input():
    user_input = input("Podaj datę (YYYY-mm-dd). Wciśnij Enter, aby wybrać jutro: ")

    if not user_input:
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%d")
    return user_input


if __name__ == "__main__":

    forecast = WeatherForecast()
    searched_date = get_date_input()
    print(f"\n--- Sprawdzanie dla daty: {searched_date} ---")

    result = forecast[searched_date]
    print(f"Ostateczny wynik dla {searched_date}: {result}")

    print("\n--- Znane dane (iterator) ---")
    for date in forecast:
        print(f"Data: {date}")

    print("\n--- Pary (data, pogoda) ---")
    for date, weather in forecast.items():
        print(f"W dniu {date}: {weather}")