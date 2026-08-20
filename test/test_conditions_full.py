import requests
import pandas as pd

latitude = 34.0094
longitude = -118.4973
location_id = "SANTA_MONICA_PIER"
station_id = "9410660"


# weather
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

weather_df = pd.DataFrame(weather_response.json()["hourly"])

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

# marine

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

marine_df = pd.DataFrame(marine_response.json()["hourly"])

marine_df = marine_df.rename(columns={
    "time": "DateTime",
    "sea_surface_temperature": "WaterTempF",
    "swell_wave_height": "SwellHeightFt",
    "swell_wave_direction": "SwellDirectionDeg",
    "swell_wave_period": "SwellPeriodSec"
})

marine_df["DateTime"] = pd.to_datetime(marine_df["DateTime"])
marine_df["LocationID"] = location_id

# tides

tide_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

tide_params = {
    "product": "predictions",
    "application": "FishBook",
    "begin_date": weather_df["DateTime"].min().strftime("%Y%m%d"),
    "end_date": weather_df["DateTime"].max().strftime("%Y%m%d"),
    "datum": "MLLW",
    "station": station_id,
    "time_zone": "lst_ldt",
    "units": "english",
    "interval": "h",
    "format": "json"
}

tide_response = requests.get(tide_url, params=tide_params)
tide_response.raise_for_status()

tide_df = pd.DataFrame(tide_response.json()["predictions"])

tide_df = tide_df.rename(columns={
    "t": "DateTime",
    "v": "TideHeightFt"
})

tide_df["DateTime"] = pd.to_datetime(tide_df["DateTime"])
tide_df["TideHeightFt"] = pd.to_numeric(tide_df["TideHeightFt"])

# merge

conditions_df = pd.merge(
    weather_df,
    marine_df,
    on=["LocationID", "DateTime"],
    how="outer"
)

conditions_df = pd.merge(
    conditions_df,
    tide_df,
    on="DateTime",
    how="left"
)

# map weather codes

def weather_label(code):
    if pd.isna(code):
        return None

    code = int(code)

    if code == 0:
        return "Sunny"
    elif code in [1, 2]:
        return "Partly Cloudy"
    elif code == 3:
        return "Cloudy"
    elif code in [45, 48]:
        return "Fog"
    elif code in [51, 53, 55, 56, 57]:
        return "Drizzle"
    elif code in [61, 63, 65, 66, 67, 80, 81, 82]:
        return "Raining"
    elif code in [71, 73, 75, 77, 85, 86]:
        return "Snow"
    elif code in [95, 96, 99]:
        return "Thunderstorm"
    else:
        return "Other"


conditions_df["Weather"] = conditions_df["WeatherCode"].apply(weather_label)

# wave energy

swell_height_m = conditions_df["SwellHeightFt"] * 0.3048

conditions_df["WaveEnergyKJ"] = (
    2
    * swell_height_m**2
    * conditions_df["SwellPeriodSec"]**2
)

# cleanup

conditions_df = conditions_df.sort_values(
    ["LocationID", "DateTime"]
).reset_index(drop=True)

final_columns = [
    "LocationID",
    "DateTime",
    "Weather",
    "WeatherCode",
    "AirTempF",
    "PrecipProbability",
    "WindSpeedMph",
    "WindDirectionDeg",
    "WaterTempF",
    "SwellHeightFt",
    "SwellDirectionDeg",
    "SwellPeriodSec",
    "WaveEnergyKJ",
    "TideHeightFt"
]

conditions_df = conditions_df[final_columns]

print(conditions_df)

conditions_df.to_csv(
    "data/conditions_live.csv",
    index=False
)