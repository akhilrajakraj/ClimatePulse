import pytest

import requests

from unittest.mock import patch

from pipeline_v1 import main



def test_pipeline_stops_when_extraction_fails():
    # using context manager to simulate all functions together
    
    """To test whether the downstream execution stops if the extaction fails. """
    
    with patch(
        "pipeline_v1.fetch_weather",
        side_effect=requests.Timeout("Connection Timeout.")
        ) as mock_fetch, patch(
            "pipeline_v1.validate_weather"
        ) as mock_validate, patch(
            "pipeline_v1.save_raw_json"
        ) as mock_save_raw, patch(
            "pipeline_v1.transform_weather"
        ) as mock_transform, patch(
            "pipeline_v1.save_csv"
        ) as mock_save_csv:
            
            with pytest.raises(requests.Timeout):
                main()
                
                mock_fetch.assert_called_once
                
                mock_validate.assert_not_called
                mock_save_raw.assert_not_called
                mock_transform.assert_not_called
                mock_save_csv.assert_not_called
                
                
        
        
       