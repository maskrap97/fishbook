from src.api import build_conditions_for_location

conditions_df = build_conditions_for_location(
    latitude=34.0094,
    longitude=-118.4973,
    location_id="SANTA_MONICA_PIER",
    station_id="9410660"
)

print(conditions_df.head())
print()
print(conditions_df.tail())
print()
print("Rows:", len(conditions_df))