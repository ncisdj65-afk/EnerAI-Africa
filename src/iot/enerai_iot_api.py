from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

from src.iot.enerai_decision_engine import compute_hybrid_energy_decision


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "iot"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = DATA_DIR / "enerai_box_measurements.csv"


app = FastAPI(
    title="EnerAI-Box IoT API",
    description=(
        "API locale pour recevoir les mesures ESP32, "
        "combiner les données IoT avec le contexte IA EnerAI-Africa, "
        "et retourner une décision énergétique hybride."
    ),
    version="0.3.0"
)


class SensorPayload(BaseModel):
    device_id: str
    temperature_c: float
    humidity_percent: float
    light_raw: int
    light_percent: float
    relay_state: Optional[str] = None
    decision: Optional[str] = None


@app.get("/")
def root():
    return {
        "status": "running",
        "project": "EnerAI-Africa",
        "component": "EnerAI-Box IoT API",
        "version": "0.3.0",
        "decision_engine": "hybrid_ai_iot_energy_decision"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "api": "EnerAI-Box IoT API",
        "version": "0.3.0"
    }


@app.post("/sensor-data")
def receive_sensor_data(payload: SensorPayload):
    received_at = datetime.now(timezone.utc).isoformat()

    control = compute_hybrid_energy_decision(
        temperature_c=payload.temperature_c,
        humidity_percent=payload.humidity_percent,
        light_percent=payload.light_percent,
    )

    row = {
        "received_at": received_at,
        "device_id": payload.device_id,
        "temperature_c": payload.temperature_c,
        "humidity_percent": payload.humidity_percent,
        "light_raw": payload.light_raw,
        "light_percent": payload.light_percent,

        # État et décision envoyés par l'ESP32 avant décision Python
        "edge_relay_state": payload.relay_state,
        "edge_decision": payload.decision,

        # Décision hybride Python
        "python_relay_command": control["relay_command"],
        "python_energy_mode": control["energy_mode"],
        "python_decision": control["decision"],
        "priority": control["priority"],
        "reason": control["reason"],

        # Contexte énergétique IA / historique
        "predicted_consumption": control["predicted_consumption"],
        "forecast_source": control["forecast_source"],
        "demand_level": control["demand_level"],
        "demand_reference_low": control["demand_reference_low"],
        "demand_reference_high": control["demand_reference_high"],

        # Contexte solaire / météo locale
        "solar_estimate": control["solar_estimate"],
        "solar_status": control["solar_status"],
        "temperature_status": control["temperature_status"],
        "local_light_status": control["local_light_status"],
    }

    df_new = pd.DataFrame([row])

    if CSV_PATH.exists():
        df_existing = pd.read_csv(CSV_PATH)
        df_all = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(CSV_PATH, index=False)

    return {
        "status": "success",
        "message": "Sensor data received and hybrid AI-IoT decision computed",

        # Champs directement utilisés par l'ESP32
        "relay_command": control["relay_command"],
        "energy_mode": control["energy_mode"],
        "decision": control["decision"],
        "priority": control["priority"],

        # Champs explicatifs pour la démo et la candidature
        "reason": control["reason"],
        "predicted_consumption": control["predicted_consumption"],
        "forecast_source": control["forecast_source"],
        "demand_level": control["demand_level"],
        "solar_estimate": control["solar_estimate"],
        "solar_status": control["solar_status"],
        "temperature_status": control["temperature_status"],
        "local_light_status": control["local_light_status"],

        "saved_to": str(CSV_PATH),
        "data": row
    }


@app.get("/latest")
def latest_measurements(limit: int = 10):
    if not CSV_PATH.exists():
        return {
            "status": "empty",
            "message": "No measurements received yet."
        }

    df = pd.read_csv(CSV_PATH)

    return {
        "status": "success",
        "count": min(limit, len(df)),
        "data": df.tail(limit).to_dict(orient="records")
    }