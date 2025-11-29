import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.weather_service import WeatherService

"""
Weather Service Test Script.

This script manually tests the WeatherService by fetching coordinates for a city
and then retrieving weather data for those coordinates.
"""

def test_weather_service():
    """
    Runs a manual test of the weather service.
    """
    service = WeatherService()
    
    print("Testing Geocoding...")
    city = "Berlin"
    coords = service.get_coordinates(city)
    if coords:
        print(f"Success: {city} -> {coords}")
        lat, lon, name = coords
        
        print("\nTesting Weather Fetch...")
        weather = service.get_weather(lat, lon)
        if weather:
            print("Success: Weather data fetched")
            print(f"Current Temp: {weather['current']['temp']}°C")
            print(f"Current Desc: {weather['current']['desc']}")
            print("Forecast:")
            for day in weather['daily']:
                print(f"  {day['day']}: {day['max_temp']}°/{day['min_temp']}° - {day['desc']}")
        else:
            print("Failed to fetch weather")
    else:
        print("Failed to fetch coordinates")

if __name__ == "__main__":
    test_weather_service()
