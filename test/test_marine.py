import requests
import pandas as pd

latitude = 34.0094
longitude = -118.4973

url = "https://marine-api.open-meteo.com/v1/marine"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": (
        "sea_surface_temperature,"
        "swell_wave_height,"
        "swell_wave_direction,"
        "swell_wave_period"
    ),
    "temperature_unit": "fahrenheit",
    "length_unit": "imperial",
    "timezone": "America/Los_Angeles"
}

response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()

marine_df = pd.DataFrame(data["hourly"])

marine_df = marine_df.rename(columns = {
    "time": "DateTime",
    "sea_surface_temperature": "WaterTempF",
    "swell_wave_height": "SwellHeightFt",
    "swell_wave_direction": "SwellDirectionDeg",
    "swell_wave_period": "SwellPeriodSec"
})

marine_df["LocationID"] = "SANTA_MONICA_PIER"
marine_df["DateTime"] = pd.to_datetime(marine_df["DateTime"])

print(marine_df)