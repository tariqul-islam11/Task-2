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

    def get(self, request):
        today = datetime.now()
        start_date = today.strftime('%Y-%m-%d')
        end_date = start_date 

        dhaka_coords = {"lat": 23.8103, "lon": 90.4125}
        sylhet_coords = {"lat": 24.8944, "lon": 91.8687}

        current_weather_dhaka = get_weather_data(dhaka_coords['lat'], dhaka_coords['lon'], start_date=start_date, end_date=end_date)
        current_temp_dhaka = current_weather_dhaka['hourly']['temperature_2m'][14] #[datetime.now().hour]

        current_weather_sylhet = get_weather_data(sylhet_coords['lat'], sylhet_coords['lon'], start_date=start_date, end_date=end_date)
        current_temp_sylhet = current_weather_sylhet['hourly']['temperature_2m'][14] #[datetime.now().hour]

        forecast_weather_dhaka = get_weather_data(dhaka_coords['lat'], dhaka_coords['lon'], start_date=start_date, end_date=end_date)
        forecast_temp_dhaka = forecast_weather_dhaka['hourly']['temperature_2m'][14]

        forecast_weather_sylhet = get_weather_data(sylhet_coords['lat'], sylhet_coords['lon'], start_date=start_date, end_date=end_date)
        forecast_temp_sylhet = forecast_weather_sylhet['hourly']['temperature_2m'][14]

        if isinstance(current_temp_dhaka, (float, int)) and isinstance(forecast_temp_sylhet, (float, int)):
            if forecast_temp_sylhet > forecast_temp_dhaka:
                decision = "The temperature in Sylhet is higher than in Dhaka. You should not visit Sylhet."
            else:
                decision = "The temperature in Sylhet is lower than in Dhaka. You should visit Sylhet."
        else:
            decision = "Error: Temperature data is not in the expected format."

        return Response({
            "current_temp_dhaka": current_temp_dhaka,
            "forecast_temp_dhaka": forecast_temp_dhaka,
            "current_temp_sylhet": current_temp_sylhet,
            "forecast_temp_sylhet": forecast_temp_sylhet,
            "decision": decision
        }, status=status.HTTP_200_OK)