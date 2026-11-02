
import pytest

from pipeline_v1 import (
    validate_weather,
    transform_weather
)



sample_weather_data = {
    "latitude": 9.2648,
    "longitude": 76.7870,
    "timezone": "Asia/Kolkata",

    "hourly": {
        "time": [
            "2026-10-30T09:00",
            "2026-10-30T10:00"
        ],
        "temperature_2m": [
            28.5,
            29.0
        ],
        "precipitation": [
            0.0,
            0.2
        ]
    }
}



def test_valid_weather_response():
    validate_weather(sample_weather_data)


def test_missing_temperature():
    invalid_data = {
        "hourly": {
            "time": ["2026-10-30T09:00"],
            "precipitation": [0.0]
        }
    }

    with pytest.raises(ValueError):
        validate_weather(invalid_data)


def test_different_array_lengths():
    invalid_data = {
        "hourly": {
            "time": [
                "2026-10-30T09:00",
                "2026-10-30T10:00"
            ],
            "temperature_2m": [28.5],
            "precipitation": [0.0, 0.2]
        }
    }

    with pytest.raises(ValueError):
        validate_weather(invalid_data)


def test_empty_timestamps():
    invalid_data = {
        "hourly": {
            "time": [],
            "temperature_2m": [],
            "precipitation": []
        }
    }

    with pytest.raises(ValueError):
        validate_weather(invalid_data)


def test_transform_weather():
    rows = transform_weather(sample_weather_data)

    assert len(rows) == 2
    assert rows[0]["temperature_c"] == 28.5
    assert rows[1]["precipitation_mm"] == 0.2
    
def test_missing_latitude():
    
    invalid_data = sample_weather_data.copy()
    invalid_data.pop("latitude")

    with pytest.raises(ValueError, match="Latitude"):
        validate_weather(invalid_data)
        
def test_invalid_timezone():
    
    invalid_data = sample_weather_data.copy()
    invalid_data["timezone"] = ""
    
    with pytest.raises(ValueError, match="Timezone"):
        validate_weather(invalid_data)
        
def test_non_numeric_coordinates():
    
    invalid_data = sample_weather_data.copy()
    invalid_data["latitude"] = "Kerala"
    
    with pytest.raises(ValueError, match="Latitude"):
        validate_weather(invalid_data)
        

        