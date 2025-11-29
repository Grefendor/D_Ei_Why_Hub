"""
Weather Service Module.

This module provides the `WeatherService` class, which interfaces with the Open-Meteo API
to fetch current weather conditions and forecasts. It handles geocoding of city names
and mapping of WMO weather codes to human-readable descriptions and icons.
"""

import requests
from datetime import datetime

class WeatherService:
    """
    Handles interactions with the Open-Meteo weather API.

    Attributes:
        geocoding_url (str): API endpoint for geocoding city names.
        forecast_url (str): API endpoint for weather forecasts.
        wmo_codes (Dict[int, Tuple[str, str]]): Mapping of WMO codes to descriptions and icons.
    """

    def __init__(self):
        """Initializes the WeatherService with API endpoints and WMO code mappings."""
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"
        
        # WMO Weather interpretation codes (WW)
        self.wmo_codes = {
            0: ("Clear sky", "☀️"),
            1: ("Mainly clear", "🌤️"),
            2: ("Partly cloudy", "bq️"),
            3: ("Overcast", "☁️"),
            45: ("Fog", "🌫️"),
            48: ("Depositing rime fog", "🌫️"),
            51: ("Light Drizzle", "aa"),
            53: ("Moderate Drizzle", "aa"),
            55: ("Dense Drizzle", "aa"),
            56: ("Light Freezing Drizzle", "aa"),
            57: ("Dense Freezing Drizzle", "aa"),
            61: ("Slight Rain", "🌧️"),
            63: ("Moderate Rain", "🌧️"),
            65: ("Heavy Rain", "🌧️"),
            66: ("Light Freezing Rain", "🌧️"),
            67: ("Heavy Freezing Rain", "🌧️"),
            71: ("Slight Snow", "❄️"),
            73: ("Moderate Snow", "❄️"),
            75: ("Heavy Snow", "❄️"),
            77: ("Snow Grains", "❄️"),
            30: ("Slight Rain Showers", "aa"),
            31: ("Moderate Rain Showers", "aa"),
            32: ("Violent Rain Showers", "aa"),
            33: ("Slight Snow Showers", "❄️"),
            34: ("Heavy Snow Showers", "❄️"),
            95: ("Thunderstorm", "⛈️"),
            96: ("Thunderstorm with Hail", "⛈️"),
            99: ("Thunderstorm with Heavy Hail", "⛈️"),
        }

    def get_coordinates(self, city_name):
        """
        Fetches the geographic coordinates for a given city name.

        Args:
            city_name (str): The name of the city to search for.

        Returns:
            tuple: A tuple containing (latitude, longitude, name) if found, otherwise None.
        """
        try:
            params = {
                "name": city_name,
                "count": 1,
                "language": "en",
                "format": "json"
            }
            response = requests.get(self.geocoding_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data and data["results"]:
                result = data["results"][0]
                return result["latitude"], result["longitude"], result["name"]
            return None
        except Exception as e:
            print(f"Error fetching coordinates: {e}")
            return None

    def get_weather(self, lat, lon):
        """
        Fetches current weather and forecast data for specific coordinates.

        Args:
            lat (float): Latitude.
            lon (float): Longitude.

        Returns:
            dict: A dictionary containing 'current' and 'daily' weather data, or None on error.
        """
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                "timezone": "auto"
            }
            response = requests.get(self.forecast_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            daily = data.get("daily", {})
            
            weather_data = {
                "current": {
                    "temp": current.get("temperature_2m"),
                    "code": current.get("weather_code"),
                    "desc": self.get_weather_desc(current.get("weather_code")),
                    "icon": self.get_weather_icon(current.get("weather_code"))
                },
                "daily": []
            }
            
            # Process daily forecast (next 3 days)
            if daily:
                times = daily.get("time", [])
                codes = daily.get("weather_code", [])
                max_temps = daily.get("temperature_2m_max", [])
                min_temps = daily.get("temperature_2m_min", [])
                
                # Start from index 1 (tomorrow) up to 3 days
                for i in range(1, min(4, len(times))):
                    date_obj = datetime.strptime(times[i], "%Y-%m-%d")
                    day_name = date_obj.strftime("%a") # Mon, Tue, etc.
                    
                    weather_data["daily"].append({
                        "day": day_name,
                        "code": codes[i],
                        "desc": self.get_weather_desc(codes[i]),
                        "icon": self.get_weather_icon(codes[i]),
                        "max_temp": max_temps[i],
                        "min_temp": min_temps[i]
                    })
                    
            return weather_data
            
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None

    def get_weather_desc(self, code):
        """Returns the text description for a given WMO weather code."""
        return self.wmo_codes.get(code, ("Unknown", "?"))[0]

    def get_weather_icon(self, code):
        """Returns the icon/emoji for a given WMO weather code."""
        return self.wmo_codes.get(code, ("Unknown", "?"))[1]
