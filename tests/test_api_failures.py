import requests
import pytest

from unittest.mock import patch

from pipeline_v1 import (
    fetch_weather,
)

@patch("pipeline_v1.requests.get")
def test_API_timeout(mock_get):
    
    mock_get.side_effect = requests.Timeout(
        "Connection Timeout."
    )
    
    with pytest.raises(requests.Timeout):
        fetch_weather()
        
    mock_get.assert_called_once() 
    

@patch("pipeline_v1.requests.get")
def test_api_internal_error(mock_get):

    # Create a simulated HTTP response
    mock_response = mock_get.return_value

    # Simulate HTTP 500
    mock_response.raise_for_status.side_effect = requests.HTTPError(
        "500 Internal Server Error"
    )

    # Verify that fetch_weather raises HTTPError
    with pytest.raises(requests.HTTPError):
        fetch_weather()

    # Verify that the correct methods were called
    mock_get.assert_called_once()
    mock_response.raise_for_status.assert_called_once()

    
@patch("pipeline_v1.requests.get")
def test_invalid_api_response(mock_get):
    
    mock_response = mock_get.return_value
    
    mock_response.raise_for_status.return_value = None
    
    mock_response.json.side_effect = ValueError(
        "Invalid JSON data."
    )
    
    with pytest.raises(ValueError, match="Invalid JSON"):
        fetch_weather()
        
    mock_response.json.assert_called_once()
    

@patch("pipeline_v1.requests.get")
def test_missing_hourly_data(mock_get):

    mock_response = mock_get.return_value

    mock_response.raise_for_status.return_value = None

    mock_response.json.return_value = {
        "latitude": 9.2648,
        "longitude": 76.7870,
        "timezone": "Asia/Kolkata"
    }

    with pytest.raises(ValueError, match="hourly"):
        fetch_weather()

    mock_response.json.assert_called_once()
