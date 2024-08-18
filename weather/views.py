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
# from .serializers import DistrictTemperatureSerializer

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
        # serializer = DistrictTemperatureSerializer(districts, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)

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
        
            print(f"Printing dis : {district['lat']}")
            lat = district['lat']
            lon = district['long']
            weather_data = get_weather_data(lat, lon, start_date, end_date)
            avg_temp = calculate_average_2pm_temperature(weather_data)
            print(f"avg_temp : {avg_temp}")
            district_temperatures.append({
                "district": district['name'],
                "latitude": lat,
                "longitude": lon,
                "average_temperature_2pm": avg_temp
            })

        coolest = sorted(district_temperatures, key=lambda x: x['average_temperature_2pm'])[:10]
        print(f"coolest : {coolest}")
        # serializer = DistrictTemperatureSerializer(coolest, many=True)
        return Response({"coolest_districts": coolest}, status=status.HTTP_200_OK)

        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
