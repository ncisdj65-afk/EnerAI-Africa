from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = PROJECT_ROOT / "models" / "random_forest_v3_corrected_weather_solar.pkl"
DEFAULT_HISTORY_PATH = PROJECT_ROOT / "data" / "processed" / "df_model_v3_corrected_weather_solar.csv"

WEATHER_FEATURES = [
    "temperature_2m",
    "relative_humidity_2m",
    "surface_pressure",
    "wind_speed_10m",
]

SOLAR_FEATURE = "solar_irradiance"


def load_model(model_path=MODEL_PATH):
    """
    Charge le modèle Random Forest v3 et ses métadonnées.
    """
    if not model_path.exists():
        raise FileNotFoundError(f"Modèle introuvable : {model_path}")

    return joblib.load(model_path)


def load_history(history_path=DEFAULT_HISTORY_PATH):
    """
    Charge l'historique utilisé pour construire les variables de prédiction.
    """
    if not history_path.exists():
        raise FileNotFoundError(f"Historique introuvable : {history_path}")

    history_df = pd.read_csv(history_path)

    history_df["timestamp"] = pd.to_datetime(
        history_df["timestamp"],
        utc=True,
        errors="coerce"
    )

    history_df = (
        history_df
        .dropna(subset=["timestamp", "conso_horaire"])
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    return history_df


def build_hourly_profile(history_df, column_name):
    """
    Construit un profil moyen par mois et par heure.
    Sert de fallback lorsqu'on n'a pas encore de prévisions météo/solaire futures.
    """
    profile = (
        history_df
        .assign(
            month=history_df["timestamp"].dt.month,
            hour=history_df["timestamp"].dt.hour
        )
        .groupby(["month", "hour"])[column_name]
        .mean()
    )

    fallback_by_hour = (
        history_df
        .assign(hour=history_df["timestamp"].dt.hour)
        .groupby("hour")[column_name]
        .mean()
    )

    global_mean = history_df[column_name].mean()

    return profile, fallback_by_hour, global_mean


def get_profile_value(timestamp, profile, fallback_by_hour, global_mean):
    """
    Retourne une valeur de profil pour un timestamp futur.
    """
    month = timestamp.month
    hour = timestamp.hour

    if (month, hour) in profile.index:
        return profile.loc[(month, hour)]

    if hour in fallback_by_hour.index:
        return fallback_by_hour.loc[hour]

    return global_mean


def prepare_next_24h_features(history_df):
    """
    Prépare les variables nécessaires pour prédire les 24 prochaines heures.

    Le modèle v3 utilise :
    - hour
    - dayofweek
    - month
    - lag_1
    - lag_24
    - rolling_24
    - solar_irradiance
    - temperature_2m
    - relative_humidity_2m
    - surface_pressure
    - wind_speed_10m

    Cette version utilise des profils historiques moyens pour météo et solaire.
    Pour une version production, ces colonnes devront venir de prévisions météo/solaire réelles.
    """
    required_columns = [
        "timestamp",
        "conso_horaire",
        SOLAR_FEATURE,
        *WEATHER_FEATURES,
    ]

    missing_columns = [col for col in required_columns if col not in history_df.columns]

    if missing_columns:
        raise ValueError(f"Colonnes manquantes dans l'historique : {missing_columns}")

    history_df = history_df.copy()

    history_df["timestamp"] = pd.to_datetime(
        history_df["timestamp"],
        utc=True,
        errors="coerce"
    )

    history_df = (
        history_df
        .dropna(subset=required_columns)
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    if len(history_df) < 24:
        raise ValueError("L'historique doit contenir au moins 24 heures de données.")

    model_bundle = load_model()
    model = model_bundle["model"]
    features = model_bundle["features"]

    last_timestamp = history_df["timestamp"].max()

    future_timestamps = pd.date_range(
        start=last_timestamp + pd.Timedelta(hours=1),
        periods=24,
        freq="h",
        tz="UTC"
    )

    profiles = {}

    for col in [SOLAR_FEATURE, *WEATHER_FEATURES]:
        profiles[col] = build_hourly_profile(history_df, col)

    conso_history = history_df["conso_horaire"].tolist()
    future_rows = []

    for future_timestamp in future_timestamps:
        row = {
            "timestamp": future_timestamp,
            "hour": future_timestamp.hour,
            "dayofweek": future_timestamp.dayofweek,
            "month": future_timestamp.month,
            "lag_1": conso_history[-1],
            "lag_24": conso_history[-24],
            "rolling_24": sum(conso_history[-24:]) / 24,
        }

        for col in [SOLAR_FEATURE, *WEATHER_FEATURES]:
            profile, fallback_by_hour, global_mean = profiles[col]
            row[col] = get_profile_value(
                timestamp=future_timestamp,
                profile=profile,
                fallback_by_hour=fallback_by_hour,
                global_mean=global_mean
            )

        X_future_one_step = pd.DataFrame([row])[features]
        predicted_value = model.predict(X_future_one_step)[0]

        row["predicted_conso_horaire"] = predicted_value

        conso_history.append(predicted_value)
        future_rows.append(row)

    future_df = pd.DataFrame(future_rows)

    return future_df


def predict_next_24h(history_df=None):
    """
    Produit une prédiction horaire pour les 24 prochaines heures.
    """
    if history_df is None:
        history_df = load_history()

    future_df = prepare_next_24h_features(history_df)

    result = future_df[
        [
            "timestamp",
            "predicted_conso_horaire",
            "solar_irradiance",
            "temperature_2m",
            "relative_humidity_2m",
            "surface_pressure",
            "wind_speed_10m",
        ]
    ].copy()

    return result


def main():
    predictions = predict_next_24h()

    print("Prédictions des 24 prochaines heures avec le modèle v3 :")
    print(predictions.to_string(index=False))


if __name__ == "__main__":
    main()