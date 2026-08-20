import requests
import pandas as pd

station_id = "9410660"

url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

params = {
    "product": "predictions",
    "application": "FishBook",
    "begin_date": "20260818",
    "end_date": "20260825",
    "datum": "MLLW",
    "station": station_id,
    "time_zone": "lst_ldt",
    "units": "english",
    "interval": "h",
    "format": "json"
}

response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()

tide_df = pd.DataFrame(data["predictions"])

tide_df = tide_df.rename(columns={
    "t": "DateTime",
    "v": "TideHeightFt"
})

tide_df["DateTime"] = pd.to_datetime(tide_df["DateTime"])
tide_df["TideHeightFt"] = pd.to_numeric(tide_df["TideHeightFt"])

print(tide_df)