
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

    try:
        response = requests.get(
            API_URL,
            params = PARAMS,
            timeout = 30
        )
        
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        data = response.json()
        
        if not isinstance(data, dict):
            raise ValueError("API response must be a dictionary.")
        
        if "hourly" not in data:
            raise ValueError("API response missing 'hourly' field.")
        
        logger.info("Weather data fetched successfully.")
        return data
    
    except requests.Timeout:
        logger.error("Request timed out.")
        raise
    
    except requests.HTTPError as error:
        logger.error("HTTP error occurred: %s", error)
        raise
    
    except requests.RequestException as error:
        logger.error("Request failed: %s", error)
        raise

    except ValueError as error:
        logger.error("Data validation error: %s", error)
        raise
    
    
def validate_weather(data):
    
    """Validates the content and structure of the API data."""
    
    if not isinstance(data, dict):
        raise ValueError("API reposnse must be a dictionary.")

    required_metadata = [
        "latitude",
        "longitude",
        "timezone",
    ]
    
    for field in required_metadata: 
        if field not in data:
            raise ValueError(f"Missing meta data field:{field.capitalize()}")
        
    if not isinstance(data["latitude"], (int, float)):
        raise ValueError("Latitude must be numeric.")

    if not isinstance(data["longitude"], (int, float)):
        raise ValueError("Longitude must be numeric. ")
    
    if not isinstance(data["timezone"], str) or not data["timezone"].strip():
        raise ValueError("Timezone must be a non empty string.")

    if "hourly" not in data or not isinstance(data["hourly"], dict):
        raise ValueError("Missing or invalide hour data.")
    
    hourly = data["hourly"]
    
    required_field = [
        "time",
        "temperature_2m",
        "precipitation",
    ]
    
    for field in required_field: 
        if field not in hourly:            
            raise ValueError(f"Missing hourly field: {field}")
        
        if not isinstance(hourly[field], list):
            raise ValueError(f"{field} must be in list.")
        
    lengths = [
        len(hourly["time"]),
        len(hourly["temperature_2m"]),
        len(hourly["precipitation"])
    ]
    
    if len(set(lengths)) != 1:
        raise ValueError("Weather arrays have different length.")
    
    if not hourly["time"]:
        raise ValueError("Weather array does not have timestamp.")
    
    logger.info("Weather data validated successfully.")
    
    return True    
    
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
