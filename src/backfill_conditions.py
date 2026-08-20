import pandas as pd
from pathlib import Path

from src.api import (
    get_historical_weather,
    get_historical_marine,
    get_tides,
    weather_label
)


# -------------------------
# Settings
# -------------------------

BACKFILL_START = "2026-07-01"

today = pd.Timestamp.now(
    tz="America/Los_Angeles"
).tz_localize(None).normalize()

BACKFILL_END = (today - pd.Timedelta(days=1)).strftime("%Y-%m-%d")

default_station_id = "9410660"

locations_df = pd.read_csv("data/locations.csv")

all_conditions = []


# -------------------------
# Process each location
# -------------------------

for index, row in locations_df.iterrows():

    location_id = row["LocationID"]
    latitude = row["Latitude"]
    longitude = row["Longitude"]
    tide_offset_ft = row["TideOffsetFt"]

    print(
        f"Processing {index + 1}/{len(locations_df)}: "
        f"{location_id}"
    )

    # Historical weather
    weather_df = get_historical_weather(
        latitude=latitude,
        longitude=longitude,
        location_id=location_id,
        start_date=BACKFILL_START,
        end_date=BACKFILL_END
    )

    # Historical marine
    marine_df = get_historical_marine(
        latitude=latitude,
        longitude=longitude,
        location_id=location_id,
        start_date=BACKFILL_START,
        end_date=BACKFILL_END
    )

    # NOAA tides
    tide_df = get_tides(
        default_station_id,
        pd.Timestamp(BACKFILL_START),
        pd.Timestamp(BACKFILL_END)
    )

    # Merge weather + marine
    conditions_df = pd.merge(
        weather_df,
        marine_df,
        on=["LocationID", "DateTime"],
        how="outer"
    )

    # Add tides
    conditions_df = pd.merge(
        conditions_df,
        tide_df,
        on="DateTime",
        how="left"
    )

    # Apply local tide adjustment
    conditions_df["TideHeightFt"] = (
        conditions_df["TideHeightFt"]
        + tide_offset_ft
    )

    # Weather description
    conditions_df["Weather"] = (
        conditions_df["WeatherCode"]
        .apply(weather_label)
    )

    # Wave energy
    swell_height_m = (
        conditions_df["SwellHeightFt"] * 0.3048
    )

    conditions_df["WaveEnergyKJ"] = (
        2
        * swell_height_m**2
        * conditions_df["SwellPeriodSec"]**2
    )

    conditions_df["DataType"] = "Historical"

    all_conditions.append(conditions_df)


# -------------------------
# Combine locations
# -------------------------

backfill_df = pd.concat(
    all_conditions,
    ignore_index=True
)

backfill_df = backfill_df.sort_values(
    ["LocationID", "DateTime"]
).reset_index(drop=True)


# -------------------------
# Merge with existing data
# -------------------------

output_path = Path("data/conditions_live.csv")

existing_df = pd.read_csv(
    output_path,
    parse_dates=["DateTime"]
)

combined_df = pd.concat(
    [existing_df, backfill_df],
    ignore_index=True
)

# Backfill was added last, so historical data replaces
# any previously stored forecasts for overlapping timestamps.
combined_df = combined_df.drop_duplicates(
    subset=["LocationID", "DateTime"],
    keep="last"
)

combined_df = combined_df.sort_values(
    ["LocationID", "DateTime"]
).reset_index(drop=True)


# -------------------------
# Save
# -------------------------

combined_df.to_csv(
    output_path,
    index=False
)

print()
print("Historical backfill complete.")
print("Backfill start:", BACKFILL_START)
print("Backfill end:", BACKFILL_END)
print("Locations processed:", len(locations_df))
print("Historical rows fetched:", len(backfill_df))
print("Total stored rows:", len(combined_df))
print(
    "Stored date range:",
    combined_df["DateTime"].min(),
    "to",
    combined_df["DateTime"].max()
)