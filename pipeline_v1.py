
import csv
import json
import logging
from datetime import datetime
from pathlib import Path

import requests

# Project paths
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

API_URL = "https://api.open-meteo.com/v1/forecast"

PARAMS = {
    "latitude": 9.2648,
    "longitude": 76.7870,
    "hourly": "temperature_2m,precipitation",
    "forecast_days": 3,
    "timezone": "Asia/Kolkata",
}


def fetch_weather():
    """Extract weather data from the API."""
    logger.info("Requesting weather data...")

    response = requests.get(
        API_URL,
        params=PARAMS,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict) or "hourly" not in data:
        raise ValueError("API response is missing the hourly data section.")

    logger.info("Weather data retrieved successfully.")
    return data


def validate_weather(data):
    """Check that required hourly fields exist and have matching lengths."""
    hourly = data["hourly"]

    required_fields = [
        "time",
        "temperature_2m",
        "precipitation",
    ]

    missing = [field for field in required_fields if field not in hourly]

    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    lengths = {field: len(hourly[field]) for field in required_fields}

    if len(set(lengths.values())) != 1:
        raise ValueError(f"Hourly arrays have different lengths: {lengths}")

    if not hourly["time"]:
        raise ValueError("The API returned no hourly records.")

    logger.info("Validation passed: %s hourly records.", len(hourly["time"]))


def save_raw_json(data, run_id):
    """Preserve the original API response."""
    path = RAW_DIR / f"weather_{run_id}.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    logger.info("Raw JSON saved to %s", path)
    return path


def transform_weather(data):
    """Convert parallel API arrays into one row per timestamp."""
    hourly = data["hourly"]
    rows = []

    for i, timestamp in enumerate(hourly["time"]):
        rows.append({
            "location": "Mavelikara",
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "timestamp": timestamp,
            "temperature_c": hourly["temperature_2m"][i],
            "precipitation_mm": hourly["precipitation"][i],
            "timezone": data["timezone"],
            "source": "Open-Meteo",
        })

    return rows


def save_csv(rows, run_id):
    """Load transformed rows into a CSV file."""
    if not rows:
        raise ValueError("Cannot save an empty dataset.")

    path = PROCESSED_DIR / f"weather_{run_id}.csv"

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Processed CSV saved to %s", path)
    return path


def main():
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        data = fetch_weather()
        validate_weather(data)

        save_raw_json(data, run_id)

        rows = transform_weather(data)
        csv_path = save_csv(rows, run_id)

        logger.info("Pipeline completed successfully.")
        logger.info("Total records processed: %s", len(rows))
        logger.info("Output file: %s", csv_path)

    except (requests.RequestException, ValueError, KeyError) as error:
        logger.error("Pipeline failed: %s", error)
        raise


if __name__ == "__main__":
    main()
