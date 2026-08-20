from src.api import (
    get_historical_weather,
    get_historical_marine
)

weather_df = get_historical_weather(
    latitude=34.0094,
    longitude=-118.4973,
    location_id="SANTA_MONICA_PIER",
    start_date="2026-07-01",
    end_date="2026-07-07"
)

marine_df = get_historical_marine(
    latitude=34.0094,
    longitude=-118.4973,
    location_id="SANTA_MONICA_PIER",
    start_date="2026-07-01",
    end_date="2026-07-07"
)

print(weather_df.head())
print(weather_df.tail())

print()

print(marine_df.head())
print(marine_df.tail())