import requests
import pandas as pd

# pull hourly weather forecasts from Open-Meteo API
def get_weather(latitude, longitude, location_id):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
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
        "timezone": "America/Los_Angeles",
        "past_days": 7
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    df = pd.DataFrame(response.json()["hourly"])

    df = df.rename(columns={
        "time": "DateTime",
        "temperature_2m": "AirTempF",
        "precipitation_probability": "PrecipProbability",
        "wind_speed_10m": "WindSpeedMph",
        "wind_direction_10m": "WindDirectionDeg",
        "weather_code": "WeatherCode"
    })

    df["DateTime"] = pd.to_datetime(df["DateTime"])
    df["LocationID"] = location_id

    return df

# pull historical hourly weather conditions from Open-Meteo API
def get_historical_weather(
    latitude,
    longitude,
    location_id,
    start_date,
    end_date
):
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
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

    response = requests.get(url, params=params)
    response.raise_for_status()

    df = pd.DataFrame(response.json()["hourly"])

    df = df.rename(columns={
        "time": "DateTime",
        "temperature_2m": "AirTempF",
        "precipitation_probability": "PrecipProbability",
        "wind_speed_10m": "WindSpeedMph",
        "wind_direction_10m": "WindDirectionDeg",
        "weather_code": "WeatherCode"
    })

    df["DateTime"] = pd.to_datetime(df["DateTime"])
    df["LocationID"] = location_id

    return df

# pull hourly marine conditions from Open-Meteo API
def get_marine(latitude, longitude, location_id):
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
        "timezone": "America/Los_Angeles",
        "past_days": 7
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    df = pd.DataFrame(response.json()["hourly"])

    df = df.rename(columns={
        "time": "DateTime",
        "sea_surface_temperature": "WaterTempF",
        "swell_wave_height": "SwellHeightFt",
        "swell_wave_direction": "SwellDirectionDeg",
        "swell_wave_period": "SwellPeriodSec"
    })

    df["DateTime"] = pd.to_datetime(df["DateTime"])
    df["LocationID"] = location_id

    return df

# Pull hourly historical marine conditions from Open-Meteo API
def get_historical_marine(
    latitude,
    longitude,
    location_id,
    start_date,
    end_date
):
    url = "https://marine-api.open-meteo.com/v1/marine"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
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

    df = pd.DataFrame(response.json()["hourly"])

    df = df.rename(columns={
        "time": "DateTime",
        "sea_surface_temperature": "WaterTempF",
        "swell_wave_height": "SwellHeightFt",
        "swell_wave_direction": "SwellDirectionDeg",
        "swell_wave_period": "SwellPeriodSec"
    })

    df["DateTime"] = pd.to_datetime(df["DateTime"])
    df["LocationID"] = location_id

    return df

# Pull hourly tide forecasts and conditions from NOAA API
def get_tides(station_id, start_date, end_date):
    url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

    params = {
        "product": "predictions",
        "application": "FishBook",
        "begin_date": start_date.strftime("%Y%m%d"),
        "end_date": end_date.strftime("%Y%m%d"),
        "datum": "MLLW",
        "station": station_id,
        "time_zone": "lst_ldt",
        "units": "english",
        "interval": "h",
        "format": "json"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    df = pd.DataFrame(response.json()["predictions"])

    df = df.rename(columns={
        "t": "DateTime",
        "v": "TideHeightFt"
    })

    df["DateTime"] = pd.to_datetime(df["DateTime"])
    df["TideHeightFt"] = pd.to_numeric(df["TideHeightFt"])

    return df

# Map weather codes to labels
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
    
# build and merge dataframes
def build_conditions_for_location(
    latitude,
    longitude,
    location_id,
    station_id,
    tide_offset_ft=0
):
    weather_df = get_weather(
        latitude,
        longitude,
        location_id
    )

    marine_df = get_marine(
        latitude,
        longitude,
        location_id
    )

    tide_df = get_tides(
        station_id,
        weather_df["DateTime"].min(),
        weather_df["DateTime"].max()
    )

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

    conditions_df["TideHeightFt"] = (
    conditions_df["TideHeightFt"] + tide_offset_ft
)

    conditions_df["Weather"] = (
        conditions_df["WeatherCode"]
        .apply(weather_label)
    )

    swell_height_m = (
        conditions_df["SwellHeightFt"] * 0.3048
    )

    conditions_df["WaveEnergyKJ"] = (
        2
        * swell_height_m**2
        * conditions_df["SwellPeriodSec"]**2
    )

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

    return conditions_df[final_columns]


