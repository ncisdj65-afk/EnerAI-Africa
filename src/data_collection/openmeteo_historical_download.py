from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "meteo"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "ndjamena_meteo_historical_2014_2019.csv"


LATITUDE = 12.11
LONGITUDE = 15.05

START_DATE = "2014-12-11"
END_DATE = "2019-05-01"

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "surface_pressure",
    "wind_speed_10m",
]


def request_openmeteo_archive(start_date, end_date):
    """
    Télécharge les données horaires historiques Open-Meteo pour N'Djamena.
    """
    base_url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(HOURLY_VARIABLES),
        "timezone": "UTC",
        "timeformat": "iso8601",
    }

    url = base_url + "?" + urlencode(params)

    print(f"Téléchargement : {start_date} → {end_date}")

    with urlopen(url) as response:
        data = json.loads(response.read().decode("utf-8"))

    if data.get("error"):
        raise RuntimeError(f"Erreur Open-Meteo : {data}")

    hourly = data.get("hourly")

    if hourly is None:
        raise RuntimeError(f"Réponse Open-Meteo sans clé 'hourly' : {data}")

    df = pd.DataFrame(hourly)

    return df


def download_by_year():
    """
    Télécharge les données par blocs annuels pour réduire le risque d'erreur API.
    """
    periods = [
        ("2014-12-11", "2014-12-31"),
        ("2015-01-01", "2015-12-31"),
        ("2016-01-01", "2016-12-31"),
        ("2017-01-01", "2017-12-31"),
        ("2018-01-01", "2018-12-31"),
        ("2019-01-01", "2019-05-01"),
    ]

    frames = []

    for start_date, end_date in periods:
        df_part = request_openmeteo_archive(start_date, end_date)
        frames.append(df_part)

    df = pd.concat(frames, ignore_index=True)

    df = df.rename(columns={"time": "timestamp"})

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
        errors="coerce"
    )

    for col in HOURLY_VARIABLES:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = (
        df
        .dropna(subset=["timestamp"])
        .sort_values("timestamp")
        .drop_duplicates(subset=["timestamp"])
        .reset_index(drop=True)
    )

    return df


def main():
    df_meteo = download_by_year()

    print("\nMétéo historique téléchargée.")
    print("Shape :", df_meteo.shape)
    print("Période :", df_meteo["timestamp"].min(), "→", df_meteo["timestamp"].max())
    print("Valeurs manquantes :")
    print(df_meteo.isna().sum())

    df_meteo.to_csv(OUTPUT_PATH, index=False)

    print("\nFichier sauvegardé :")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()