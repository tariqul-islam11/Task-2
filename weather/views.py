import requests
import statistics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import District

districts_url = "https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json"
weather_api_url = "https://api.open-meteo.com/v1/forecast"

def get_districts():
    response = requests.get(districts_url)
    response.raise_for_status()
    return response.json()

def generate_weather_params(latitude, longitude, start_date, end_date, hourly_data="temperature_2m", timezone="Asia/Dhaka"):
    return {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": hourly_data,
        "timezone": timezone,
        "start_date": start_date,
        "end_date": end_date
    }

def get_weather_data(lat, lon, start_date, end_date):
    params = generate_weather_params(lat, lon, start_date=start_date, end_date=end_date)
    response = requests.get(weather_api_url, params=params)
    response.raise_for_status()
    return response.json()

def calculate_average_2pm_temperature(weather_data):
    temperature_2pm = []
    for i in range(7):
        day_index = i * 24 + 14  
        temperature_2pm.append(weather_data['hourly']['temperature_2m'][day_index])
    return statistics.mean(temperature_2pm)

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


class DistrictListView(APIView):
    def get(self, request):
        districts = District.objects.all()

class CoolestDistrictsAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        today = datetime.now()
        start_date = today.strftime('%Y-%m-%d')
        end_date = (today + timedelta(days=6)).strftime('%Y-%m-%d')

        districts = get_districts()
        district_temperatures = []
        districts = districts['districts']
        for district in districts:
        
            #print(f"Printing dis : {district['lat']}")
            lat = district['lat']
            lon = district['long']
            district_id = district['id']
            weather_data = get_weather_data(lat, lon, start_date, end_date)
            avg_temp = calculate_average_2pm_temperature(weather_data)
            print(f"avg_temp of district id ({district_id}): {avg_temp}")
            district_temperatures.append({
                "district_id": district['id'],
                "district": district['name'],
                "latitude": lat,
                "longitude": lon,
                "average_temperature_2pm": avg_temp
            })

        coolest = sorted(district_temperatures, key=lambda x: x['average_temperature_2pm'])[:10]
        print(f"coolest : {coolest}")
        return Response({"coolest_districts": coolest}, status=status.HTTP_200_OK)


class TemperatureComparisonAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, current_district_id, destination_district_id, date, hour):
        current_district = get_district_by_id(current_district_id)
        destination_district = get_district_by_id(destination_district_id)
        hour = int(hour)
        
        if not current_district or not destination_district:
            return Response({"error": "Invalid district ID"}, status=status.HTTP_400_BAD_REQUEST)

        today = datetime.now()
        current_date = today.strftime('%Y-%m-%d')
        forecast_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')

        current_weather_current = get_weather_data(current_district['lat'], current_district['long'], current_date, current_date)
        forecast_weather_current = get_weather_data(current_district['lat'], current_district['long'], forecast_date, forecast_date)
        current_temp_current = current_weather_current['hourly']['temperature_2m'][hour]
        forecast_temp_current = forecast_weather_current['hourly']['temperature_2m'][hour]

        current_weather_destination = get_weather_data(destination_district['lat'], destination_district['long'], current_date, current_date)
        forecast_weather_destination = get_weather_data(destination_district['lat'], destination_district['long'], forecast_date, forecast_date)
        current_temp_destination = current_weather_destination['hourly']['temperature_2m'][hour]
        forecast_temp_destination = forecast_weather_destination['hourly']['temperature_2m'][hour]

        if isinstance(current_temp_current, (float, int)) and isinstance(forecast_temp_destination, (float, int)):
            if forecast_temp_destination > forecast_temp_current:
                decision = f"The temperature in {destination_district['name']} is higher than in {current_district['name']}. You should not visit the destination."
            else:
                decision = f"The temperature in {destination_district['name']} is lower than in {current_district['name']}. You should visit the destination."
        else:
            decision = "Error: Temperature data is not in the expected format."

        return Response({
            "current_district_name": current_district['name'],
            "destination_district_name": destination_district['name'],
            "current_temp_current": current_temp_current,
            "forecast_temp_current": forecast_temp_current,
            "current_temp_destination": current_temp_destination,
            "forecast_temp_destination": forecast_temp_destination,
            "decision": decision
        }, status=status.HTTP_200_OK)