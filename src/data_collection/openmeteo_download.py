import requests
import pandas as pd

url = (
    "https://archive-api.open-meteo.com/v1/archive"
    "?latitude=12.11"
    "&longitude=15.05"
    "&start_date=2020-01-01"
    "&end_date=2025-12-31"
    "&hourly=temperature_2m,relative_humidity_2m,"
    "surface_pressure,wind_speed_10m"
)

response = requests.get(url)

data = response.json()

df = pd.DataFrame(data["hourly"])

df.to_csv(
    "data/raw/meteo/ndjamena_meteo.csv",
    index=False
)

print(df.head())