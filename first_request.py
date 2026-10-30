import requests

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 9.2648,
    "longitude": 76.7870,
    "hourly": "temperature_2m,precipitation",
    "forecast_days": 3,
    "timezone": "Asia/Kolkata",
}

response = requests.get(url, params=params, timeout=30)

response.raise_for_status()  # Raise an exception for HTTP errors

data = response.json()

print("Weather Forecast Data:")
print("Timezone:", data["timezone"])
print("Hourly Field", list(data["hourly"].keys()))
print("Number of TimeStamps:", len(data["hourly"]["time"]))
