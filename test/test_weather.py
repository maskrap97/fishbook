import requests
import pandas as pd

latitude = 34.0094
longitude = -118.4973

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": "temperature_2m,precipitation_probability,wind_speed_10m,wind_direction_10m,weather_code",
    "temperature_unit": "fahrenheit",
    "wind_speed_unit": "mph",
    "timezone": "America/Los_Angeles"
}

response = requests.get(url, params = params)

data = response.json()

weather_df = pd.DataFrame(data["hourly"])

print(weather_df)