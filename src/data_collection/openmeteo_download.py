import requests
import pandas as pd

url = (
    "https://archive-api.open-meteo.com/v1/archive"
    "?latitude=12.11"
    "&longitude=15.05"
    "&start_date=2014-12-11"
    "&end_date=2019-05-01"
    "&hourly=temperature_2m,relative_humidity_2m,"
    "surface_pressure,wind_speed_10m"
)

data = requests.get(url).json()

meteo = pd.DataFrame(data["hourly"])

meteo.to_csv(
    "data/raw/meteo/ndjamena_meteo.csv",
    index=False
)

print(meteo["time"].min())
print(meteo["time"].max())
print(meteo.shape)