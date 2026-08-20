import requests
import pandas as pd

latitude = 34.0094
longitude = -118.4973
location_id = "SANTA_MONICA_PIER"

weather_url = "https://api.open-meteo.com/v1/forecast"

weather_params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": (
        "temperature_2m,"
        "precipitation_probability,"
        "wind_speed_10m,"
        "wind_direction_10m,"
        "weather_code"
    ),
    "temperature_unit": "fahrenheit",
    "wind_speed_unit": "mph",
    "timezone": "America/Los_Angeles"
}

weather_response = requests.get(weather_url, params=weather_params)
weather_response.raise_for_status()

weather_data = weather_response.json()

weather_df = pd.DataFrame(weather_data["hourly"])

weather_df = weather_df.rename(columns={
    "time": "DateTime",
    "temperature_2m": "AirTempF",
    "precipitation_probability": "PrecipProbability",
    "wind_speed_10m": "WindSpeedMph",
    "wind_direction_10m": "WindDirectionDeg",
    "weather_code": "WeatherCode"
})

weather_df["DateTime"] = pd.to_datetime(weather_df["DateTime"])
weather_df["LocationID"] = location_id

marine_url = "https://marine-api.open-meteo.com/v1/marine"

marine_params = {
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

marine_response = requests.get(marine_url, params=marine_params)
marine_response.raise_for_status()

marine_data = marine_response.json()

marine_df = pd.DataFrame(marine_data["hourly"])

marine_df = marine_df.rename(columns={
    "time": "DateTime",
    "sea_surface_temperature": "WaterTempF",
    "swell_wave_height": "SwellHeightFt",
    "swell_wave_direction": "SwellDirectionDeg",
    "swell_wave_period": "SwellPeriodSec"
})

marine_df["DateTime"] = pd.to_datetime(marine_df["DateTime"])
marine_df["LocationID"] = location_id

conditions_df = pd.merge(
    weather_df,
    marine_df,
    on=["LocationID", "DateTime"],
    how="outer"
)

conditions_df = conditions_df.sort_values(
    by=["LocationID", "DateTime"]
).reset_index(drop=True)

print(conditions_df)