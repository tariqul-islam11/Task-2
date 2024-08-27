import requests
import statistics
from .constants import districts_url, weather_api_url


# Fetches and returns the list of districts from the API.
def get_districts():
    response = requests.get(districts_url)
    response.raise_for_status()
    return response.json()

# Constructs and returns the parameters for weather API request.
def weath_params(latitude, longitude, start_date, end_date, hourly_data="temperature_2m", timezone="Asia/Dhaka"):
    return {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": hourly_data,
        "timezone": timezone,
        "start_date": start_date,
        "end_date": end_date
    }

# Retrieves and returns weather data from the API based on provided parameters.
def get_weath_data(lat, lon, start_date, end_date):
    params = weath_params(lat, lon, start_date=start_date, end_date=end_date)
    response = requests.get(weather_api_url, params=params)
    response.raise_for_status()
    return response.json()

# Calculates and returns the average temperature at 2 PM (7days).
def calc_avg_2pm_temp(weather_data):
    temperature_2pm = []
    for i in range(7):
        day_index = i * 24 + 14  
        temperature_2pm.append(weather_data['hourly']['temperature_2m'][day_index])
    return statistics.mean(temperature_2pm)

# Returns the district by ID.
def get_district_by_id(district_id):
    districts = get_districts()
    for district in districts['districts']:
        if district['id'] == str(district_id):
            return {
                'name': district['name'],
                'lat': float(district['lat']),
                'long': float(district['long'])
            }
    return None