import pandas as pd

locations_df = pd.read_csv("data/locations.csv")

print(locations_df)
print()
print("Number of locations:", len(locations_df))
print()
print(locations_df.columns.tolist())