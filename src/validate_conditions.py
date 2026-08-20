import pandas as pd

df = pd.read_csv(
    "data/conditions_live.csv",
    parse_dates=["DateTime"]
)

print("Unique locations:", df["LocationID"].nunique())

print(
    "Duplicates:",
    df.duplicated(
        subset=["LocationID", "DateTime"]
    ).sum()
)

print()
print("DataType counts:")
print(df["DataType"].value_counts())

print()
print("Null percentages:")
print((df.isna().mean() * 100).round(2))