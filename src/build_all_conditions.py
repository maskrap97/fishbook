import pandas as pd

from src.api import build_conditions_for_location
from pathlib import Path

locations_df = pd.read_csv("data/locations.csv")

all_conditions = []

default_station_id = "9410660"

for index, row in locations_df.iterrows():
    location_id = row["LocationID"]
    latitude = row["Latitude"]
    longitude = row["Longitude"]
    tide_offset_ft = row["TideOffsetFt"]

    print(
        f"Processing {index + 1}/{len(locations_df)}: "
        f"{location_id}"
    )

    conditions_df = build_conditions_for_location(
        latitude=latitude,
        longitude=longitude,
        location_id=location_id,
        station_id=default_station_id,
        tide_offset_ft=tide_offset_ft
    )

    all_conditions.append(conditions_df)


conditions_live_df = pd.concat(
    all_conditions,
    ignore_index=True
)

conditions_live_df = conditions_live_df.sort_values(
    ["LocationID", "DateTime"]
).reset_index(drop=True)



output_path = Path("data/conditions_live.csv")

# If historical data already exists, combine it with the new API pull
if output_path.exists():

    existing_df = pd.read_csv(
        output_path,
        parse_dates=["DateTime"]
    )

    combined_df = pd.concat(
        [existing_df, conditions_live_df],
        ignore_index=True
    )

    # When the same location/timestamp exists in both datasets,
    # keep the newest API pull.
    combined_df = combined_df.drop_duplicates(
        subset=["LocationID", "DateTime"],
        keep="last"
    )

else:
    combined_df = conditions_live_df


combined_df = combined_df.sort_values(
    ["LocationID", "DateTime"]
).reset_index(drop=True)

today = pd.Timestamp.now(
    tz="America/Los_Angeles"
).tz_localize(None).normalize()

combined_df["DataType"] = (
    combined_df["DateTime"]
    .apply(
        lambda x: "Historical"
        if x < today
        else "Forecast"
    )
)

combined_df.to_csv(
    output_path,
    index=False
)

print()
print("Pipeline complete.")
print("Locations processed:", len(locations_df))
print("Rows fetched this run:", len(conditions_live_df))
print("Total stored rows:", len(combined_df))
print(
    "Stored date range:",
    combined_df["DateTime"].min(),
    "to",
    combined_df["DateTime"].max()
)