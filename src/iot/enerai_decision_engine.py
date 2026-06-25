from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# EnerAI-Africa / EnerAI-Box
# Hybrid decision engine
#
# Purpose:
# Combine AI energy forecasting context + IoT sensor data
# to produce a smart relay decision.
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[2]


DATASET_CANDIDATES = [
    PROJECT_ROOT / "data" / "processed" / "df_model_v3_corrected_weather_solar.csv",
    PROJECT_ROOT / "data" / "processed" / "df_model_v3_delta_weather_solar.csv",
    PROJECT_ROOT / "data" / "processed" / "df_model_v2_weather_solar.csv",
    PROJECT_ROOT / "data" / "processed" / "consommation_hourly_corrected.csv",
]


MODEL_CANDIDATES = [
    PROJECT_ROOT / "models" / "random_forest_v3_corrected_weather_solar.pkl",
    PROJECT_ROOT / "models" / "random_forest_v3_delta_weather_solar.pkl",
    PROJECT_ROOT / "models" / "random_forest_v1.pkl",
]


TARGET_COLUMN_CANDIDATES = [
    "conso_horaire",
    "consommation_horaire",
    "consumption",
    "consumption_kwh",
    "load",
    "demand",
    "grid_import_delta",
    "delta_conso",
    "y",
]


SOLAR_COLUMN_CANDIDATES = [
    "solar_irradiance",
    "ALLSKY_SFC_SW_DWN",
    "shortwave_radiation",
    "radiation",
]


# Calibration actuelle basée sur tes valeurs observées :
# LDR cachée ≈ 0 %
# Lumière forte observée ≈ 0.44 %
#
# Ces seuils sont donc volontairement bas pour la démonstration.
# Après correction du montage LDR, on pourra les relever.
LOCAL_LIGHT_MEDIUM_PERCENT = 3.0
LOCAL_LIGHT_GOOD_PERCENT = 6.0
HIGH_TEMPERATURE_THRESHOLD_C = 38.0
HOT_TEMPERATURE_THRESHOLD_C = 35.0


@dataclass
class EnergyContext:
    predicted_consumption: float | None
    forecast_source: str
    demand_level: str
    demand_reference_low: float | None
    demand_reference_high: float | None
    solar_estimate: float | None
    solar_status: str
    temperature_status: str
    local_light_status: str


def _safe_float(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None:
            return default
        result = float(value)
        if pd.isna(result):
            return default
        return result
    except Exception:
        return default


def _first_existing_path(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


@lru_cache(maxsize=1)
def load_history_dataset() -> tuple[pd.DataFrame, str]:
    dataset_path = _first_existing_path(DATASET_CANDIDATES)

    if dataset_path is None:
        return pd.DataFrame(), "no_dataset_found"

    try:
        df = pd.read_csv(dataset_path)
        return df, str(dataset_path.relative_to(PROJECT_ROOT))
    except Exception as exc:
        return pd.DataFrame(), f"dataset_load_error: {exc}"


@lru_cache(maxsize=1)
def load_ai_model() -> tuple[Any | None, str]:
    model_path = _first_existing_path(MODEL_CANDIDATES)

    if model_path is None:
        return None, "no_model_found"

    try:
        import joblib

        model = joblib.load(model_path)
        return model, str(model_path.relative_to(PROJECT_ROOT))
    except Exception as exc:
        return None, f"model_load_error: {exc}"


def infer_target_column(df: pd.DataFrame) -> str | None:
    for column in TARGET_COLUMN_CANDIDATES:
        if column in df.columns:
            return column

    for column in df.columns:
        name = column.lower()
        if any(keyword in name for keyword in ["conso", "consumption", "load", "demand", "energy"]):
            if pd.api.types.is_numeric_dtype(df[column]):
                return column

    return None


def infer_solar_column(df: pd.DataFrame) -> str | None:
    for column in SOLAR_COLUMN_CANDIDATES:
        if column in df.columns:
            return column

    for column in df.columns:
        name = column.lower()
        if any(keyword in name for keyword in ["solar", "irradiance", "radiation", "allsky"]):
            if pd.api.types.is_numeric_dtype(df[column]):
                return column

    return None


def classify_local_light(light_percent: float) -> str:
    if light_percent >= LOCAL_LIGHT_GOOD_PERCENT:
        return "GOOD"
    if light_percent >= LOCAL_LIGHT_MEDIUM_PERCENT:
        return "MEDIUM"
    return "LOW"


def classify_temperature(temperature_c: float) -> str:
    if temperature_c >= HIGH_TEMPERATURE_THRESHOLD_C:
        return "CRITICAL"
    if temperature_c >= HOT_TEMPERATURE_THRESHOLD_C:
        return "HOT"
    return "NORMAL"


def estimate_solar_from_history(
    df: pd.DataFrame,
    now: datetime,
    light_percent: float
) -> tuple[float | None, str]:
    solar_column = infer_solar_column(df)

    if solar_column is None or df.empty:
        local_light_status = classify_local_light(light_percent)
        if local_light_status == "GOOD":
            return None, "GOOD"
        if local_light_status == "MEDIUM":
            return None, "MEDIUM"
        return None, "LOW"

    working = df.copy()

    if "hour" in working.columns:
        working = working[pd.to_numeric(working["hour"], errors="coerce") == now.hour]

    if "month" in working.columns and not working.empty:
        same_month = working[pd.to_numeric(working["month"], errors="coerce") == now.month]
        if not same_month.empty:
            working = same_month

    solar_values = pd.to_numeric(working[solar_column], errors="coerce").dropna()

    if solar_values.empty:
        return None, classify_local_light(light_percent)

    historical_solar = float(solar_values.median())

    # On combine le profil solaire historique avec la luminosité locale ESP32.
    # Si la LDR indique une lumière faible, on pénalise l'estimation.
    local_light_status = classify_local_light(light_percent)

    if local_light_status == "GOOD":
        solar_status = "GOOD"
    elif local_light_status == "MEDIUM":
        solar_status = "MEDIUM"
    else:
        solar_status = "LOW"

    return historical_solar, solar_status


def classify_demand(
    predicted_consumption: float | None,
    df: pd.DataFrame,
    target_column: str | None
) -> tuple[str, float | None, float | None]:
    if predicted_consumption is None or target_column is None or df.empty:
        return "UNKNOWN", None, None

    series = pd.to_numeric(df[target_column], errors="coerce").dropna()

    if series.empty:
        return "UNKNOWN", None, None

    low_reference = float(series.quantile(0.33))
    high_reference = float(series.quantile(0.66))

    if predicted_consumption >= high_reference:
        return "HIGH", low_reference, high_reference

    if predicted_consumption <= low_reference:
        return "LOW", low_reference, high_reference

    return "MEDIUM", low_reference, high_reference


def estimate_consumption_from_profile(
    df: pd.DataFrame,
    target_column: str | None,
    now: datetime
) -> tuple[float | None, str]:
    if df.empty or target_column is None:
        return None, "no_consumption_profile_available"

    working = df.copy()

    if "hour" in working.columns:
        same_hour = working[pd.to_numeric(working["hour"], errors="coerce") == now.hour]
        if not same_hour.empty:
            working = same_hour

    if "month" in working.columns and not working.empty:
        same_month = working[pd.to_numeric(working["month"], errors="coerce") == now.month]
        if not same_month.empty:
            working = same_month

    values = pd.to_numeric(working[target_column], errors="coerce").dropna()

    if values.empty:
        values = pd.to_numeric(df[target_column], errors="coerce").dropna()

    if values.empty:
        return None, "profile_forecast_failed"

    return float(values.median()), "historical_profile_forecast"


def build_model_feature_row(
    model: Any,
    df: pd.DataFrame,
    now: datetime,
    temperature_c: float,
    humidity_percent: float,
    light_percent: float
) -> pd.DataFrame | None:
    if df.empty:
        return None

    feature_names = getattr(model, "feature_names_in_", None)

    if feature_names is None:
        return None

    latest_row = df.dropna().tail(1)

    if latest_row.empty:
        latest_row = df.tail(1)

    if latest_row.empty:
        return None

    latest = latest_row.iloc[0]
    feature_values: dict[str, float] = {}

    solar_estimate, _ = estimate_solar_from_history(df, now, light_percent)

    for feature in feature_names:
        feature_lower = str(feature).lower()

        if feature_lower == "hour":
            feature_values[feature] = float(now.hour)

        elif feature_lower == "dayofweek":
            feature_values[feature] = float(now.weekday())

        elif feature_lower == "month":
            feature_values[feature] = float(now.month)

        elif "temperature" in feature_lower or feature_lower in ["temp", "temperature_2m"]:
            feature_values[feature] = float(temperature_c)

        elif "humidity" in feature_lower or "relative_humidity" in feature_lower:
            feature_values[feature] = float(humidity_percent)

        elif any(keyword in feature_lower for keyword in ["solar", "irradiance", "radiation", "allsky"]):
            feature_values[feature] = float(solar_estimate or 0.0)

        elif feature in df.columns:
            feature_values[feature] = _safe_float(latest[feature], 0.0) or 0.0

        else:
            feature_values[feature] = 0.0

    return pd.DataFrame([feature_values], columns=list(feature_names))


def estimate_consumption_with_model(
    df: pd.DataFrame,
    now: datetime,
    temperature_c: float,
    humidity_percent: float,
    light_percent: float
) -> tuple[float | None, str]:
    model, model_source = load_ai_model()

    if model is None:
        return None, model_source

    try:
        feature_row = build_model_feature_row(
            model=model,
            df=df,
            now=now,
            temperature_c=temperature_c,
            humidity_percent=humidity_percent,
            light_percent=light_percent,
        )

        if feature_row is None:
            return None, "model_available_but_feature_row_failed"

        prediction = model.predict(feature_row)
        return float(prediction[0]), f"ai_model_forecast:{model_source}"

    except Exception as exc:
        return None, f"model_prediction_error: {exc}"


def build_energy_context(
    temperature_c: float,
    humidity_percent: float,
    light_percent: float,
    current_time: datetime | None = None
) -> EnergyContext:
    now = current_time or datetime.now()

    df, dataset_source = load_history_dataset()
    target_column = infer_target_column(df)

    predicted_consumption, forecast_source = estimate_consumption_with_model(
        df=df,
        now=now,
        temperature_c=temperature_c,
        humidity_percent=humidity_percent,
        light_percent=light_percent,
    )

    if predicted_consumption is None:
        predicted_consumption, profile_source = estimate_consumption_from_profile(
            df=df,
            target_column=target_column,
            now=now,
        )
        forecast_source = f"{profile_source}; dataset:{dataset_source}"

    demand_level, low_ref, high_ref = classify_demand(
        predicted_consumption=predicted_consumption,
        df=df,
        target_column=target_column,
    )

    solar_estimate, solar_status = estimate_solar_from_history(
        df=df,
        now=now,
        light_percent=light_percent,
    )

    return EnergyContext(
        predicted_consumption=predicted_consumption,
        forecast_source=forecast_source,
        demand_level=demand_level,
        demand_reference_low=low_ref,
        demand_reference_high=high_ref,
        solar_estimate=solar_estimate,
        solar_status=solar_status,
        temperature_status=classify_temperature(temperature_c),
        local_light_status=classify_local_light(light_percent),
    )


def compute_hybrid_energy_decision(
    temperature_c: float,
    humidity_percent: float,
    light_percent: float
) -> dict[str, Any]:
    """
    Main hybrid decision function.

    This function combines:
    - local ESP32 temperature;
    - local ESP32 humidity;
    - local ESP32 light level;
    - AI or historical-profile electricity demand forecast;
    - historical solar context.

    The controlled relay represents a non-critical load.
    The strategy is intentionally conservative when solar availability is low.
    """

    temperature_c = float(temperature_c)
    humidity_percent = float(humidity_percent)
    light_percent = float(light_percent)

    context = build_energy_context(
        temperature_c=temperature_c,
        humidity_percent=humidity_percent,
        light_percent=light_percent,
    )

    # Rule 1: thermal protection always has priority.
    if context.temperature_status == "CRITICAL":
        relay_command = "OFF"
        energy_mode = "PROTECTION_MODE"
        decision = "HIGH_TEMPERATURE_PROTECTION_LOAD_OFF"
        priority = "HIGH"
        reason = (
            "Local temperature is critical. The non-critical load is switched off "
            "to protect the system."
        )

    # Rule 2: low solar availability.
    # For a non-critical load, low solar means the system should save energy,
    # even when the forecasted demand is low.
    elif context.solar_status == "LOW":
        relay_command = "OFF"

        if context.demand_level == "HIGH":
            energy_mode = "ECONOMY_MODE"
            decision = "HIGH_DEMAND_LOW_SOLAR_LOAD_OFF"
            priority = "HIGH"
            reason = (
                "Forecasted demand is high and local solar availability is low. "
                "The non-critical load is switched off to reduce stress on the energy system."
            )
        elif context.demand_level == "MEDIUM":
            energy_mode = "STANDBY_MODE"
            decision = "MEDIUM_DEMAND_LOW_SOLAR_STANDBY_LOAD_OFF"
            priority = "NORMAL"
            reason = (
                "Forecasted demand is moderate while local solar availability is low. "
                "The non-critical load remains off in standby mode."
            )
        elif context.demand_level == "LOW":
            energy_mode = "LOW_SOLAR_ECO_MODE"
            decision = "LOW_DEMAND_BUT_LOW_SOLAR_LOAD_OFF"
            priority = "NORMAL"
            reason = (
                "Forecasted demand is low, but local solar availability is also low. "
                "Because the relay controls a non-critical load, the system keeps it off."
            )
        else:
            energy_mode = "SAFE_LOW_SOLAR_MODE"
            decision = "UNKNOWN_DEMAND_LOW_SOLAR_LOAD_OFF"
            priority = "NORMAL"
            reason = (
                "Local solar availability is low and the demand context is uncertain. "
                "The non-critical load is switched off as a safe fallback."
            )

    # Rule 3: medium solar availability.
    elif context.solar_status == "MEDIUM":
        if context.demand_level == "HIGH":
            relay_command = "OFF"
            energy_mode = "DEMAND_RESPONSE_MODE"
            decision = "HIGH_DEMAND_MEDIUM_SOLAR_LOAD_OFF"
            priority = "HIGH"
            reason = (
                "Forecasted demand is high and solar availability is only moderate. "
                "The non-critical load is switched off to prioritize essential demand."
            )
        else:
            relay_command = "ON"
            energy_mode = "BALANCED_MODE"
            decision = "MEDIUM_SOLAR_BALANCED_LOAD_ON"
            priority = "NORMAL"
            reason = (
                "Solar availability is moderate and forecasted demand is not critical. "
                "The non-critical load is allowed in balanced mode."
            )

    # Rule 4: good solar availability.
    elif context.solar_status == "GOOD":
        if context.temperature_status == "HOT":
            relay_command = "ON"
            energy_mode = "SOLAR_SUPPORT_WITH_HEAT_MONITORING"
            decision = "GOOD_SOLAR_HOT_CONDITION_LOAD_ON_MONITORED"
            priority = "NORMAL"
            reason = (
                "Local solar availability is favorable. The load is allowed, "
                "but the system keeps monitoring temperature because conditions are hot."
            )
        elif context.demand_level == "HIGH":
            relay_command = "ON"
            energy_mode = "SOLAR_SUPPORT_MODE"
            decision = "HIGH_DEMAND_GOOD_SOLAR_LOAD_ON"
            priority = "NORMAL"
            reason = (
                "Forecasted demand is high, but local solar availability is favorable. "
                "The non-critical load can remain active in solar-support mode."
            )
        else:
            relay_command = "ON"
            energy_mode = "NORMAL_SOLAR_MODE"
            decision = "GOOD_SOLAR_LOAD_ON"
            priority = "NORMAL"
            reason = (
                "Local solar availability is favorable and no critical condition is detected. "
                "The non-critical load is allowed."
            )

    # Rule 5: safe fallback.
    else:
        relay_command = "OFF"
        energy_mode = "SAFE_FALLBACK_MODE"
        decision = "UNCERTAIN_CONTEXT_LOAD_OFF"
        priority = "NORMAL"
        reason = (
            "The energy context is uncertain. The system uses a conservative fallback "
            "and switches the non-critical load off."
        )

    return {
        "relay_command": relay_command,
        "energy_mode": energy_mode,
        "decision": decision,
        "priority": priority,
        "reason": reason,
        "predicted_consumption": context.predicted_consumption,
        "forecast_source": context.forecast_source,
        "demand_level": context.demand_level,
        "demand_reference_low": context.demand_reference_low,
        "demand_reference_high": context.demand_reference_high,
        "solar_estimate": context.solar_estimate,
        "solar_status": context.solar_status,
        "temperature_status": context.temperature_status,
        "local_light_status": context.local_light_status,
        "local_light_percent": light_percent,
        "temperature_c": temperature_c,
        "humidity_percent": humidity_percent,
    }


if __name__ == "__main__":
    test_cases = [
        {
            "name": "Low light current prototype",
            "temperature_c": 32.8,
            "humidity_percent": 64.0,
            "light_percent": 0.0,
        },
        {
            "name": "Strong light current prototype",
            "temperature_c": 32.8,
            "humidity_percent": 64.0,
            "light_percent": 0.44,
        },
        {
            "name": "High temperature protection",
            "temperature_c": 39.0,
            "humidity_percent": 66.0,
            "light_percent": 0.44,
        },
    ]

    for case in test_cases:
        print("\n---", case["name"], "---")
        result = compute_hybrid_energy_decision(
            temperature_c=case["temperature_c"],
            humidity_percent=case["humidity_percent"],
            light_percent=case["light_percent"],
        )
        for key, value in result.items():
            print(f"{key}: {value}")