from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from datetime import datetime, timedelta
from .utils import (
    get_districts,
    get_weath_data,
    calc_avg_2pm_temp,
    get_district_by_id,
)


# Base class to handle temperature data processing
class BaseTemperatureView(APIView):
    def get_temperature_data(self, start_date, end_date):
        districts = get_districts()
        district_temperatures = []
        for district in districts["districts"]:
            lat = district["lat"]
            lon = district["long"]
            weather_data = get_weath_data(lat, lon, start_date, end_date)
            avg_temp = calc_avg_2pm_temp(weather_data)
            district_temperatures.append(
                {
                    "district_id": district["id"],
                    "district": district["name"],
                    "latitude": lat,
                    "longitude": lon,
                    "average_temperature_2pm": avg_temp,
                }
            )
        return district_temperatures


# The CoolestDistrictsAPIView now inherits from the base class
class CoolestDistrictsAPIView(BaseTemperatureView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        today = datetime.now()
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=6)).strftime("%Y-%m-%d")

        district_temperatures = self.get_temperature_data(start_date, end_date)
        coolest_districts = sorted(
            district_temperatures, key=lambda x: x["average_temperature_2pm"]
        )[:10]
        return Response(
            {"coolest_districts": coolest_districts}, status=status.HTTP_200_OK
        )


# Single Responsibility Principle (SRP):
# Open/Closed Principle (OCP):
# The base class should be open for extension, but closed for modification.

class BaseTemperatureComparisonView(APIView):
    def get_temperature_comparison(self, district, hour, travel_date):
        today = datetime.now().strftime("%Y-%m-%d")
        fore_date = datetime.strptime(travel_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        curr_temp, fore_temp = self._serialize_weather_data(
            district, hour, today, fore_date
        )
        return curr_temp, fore_temp

    def _serialize_weather_data(self, district, hour, curr_date, fore_date):
        curr_weather = get_weath_data(
            district["lat"], district["long"], curr_date, curr_date
        )
        fore_weather = get_weath_data(
            district["lat"], district["long"], fore_date, fore_date
        )
        curr_temp = curr_weather["hourly"]["temperature_2m"][hour]
        fore_temp = fore_weather["hourly"]["temperature_2m"][hour]
        return curr_temp, fore_temp

    def make_decision(
        self, curr_district_name, dest_district_name, curr_fore_temp, dest_fore_temp
    ):
        if dest_fore_temp > curr_fore_temp:
            decision = (
                f"The temperature in {dest_district_name} is higher than "
                f"in {curr_district_name}. You should not visit the destination."
            )
        else:
            decision = (
                f"The temperature in {dest_district_name} is lower than "
                f"in {curr_district_name}. You should visit the destination."
            )
        return decision


# Liskov Substitution Principle (LSP):
# Derived classes should be substitutable for their base classes.


class TemperatureComparisonAPIView(BaseTemperatureComparisonView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        curr_district_id = request.query_params.get("current_district", None)
        dest_district_id = request.query_params.get("dest_district", None)
        travel_date = request.query_params.get("date", None)
        hour = int(request.query_params.get("hour", 0))

        current_district = get_district_by_id(curr_district_id)
        destination_district = get_district_by_id(dest_district_id)

        if not current_district or not destination_district:
            return Response(
                {"error": "Invalid district ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        curr_temp, fore_temp = self.get_temperature_comparison(
            current_district, hour, travel_date
        )
        curr_temp_dest, fore_temp_dest = self.get_temperature_comparison(
            destination_district, hour, travel_date
        )

        decision = self.make_decision(
            current_district["name"],
            destination_district["name"],
            fore_temp,
            fore_temp_dest,
        )

        return Response(
            {
                "current_district_name": current_district["name"],
                "destination_district_name": destination_district["name"],
                "current_temp_current": curr_temp,
                "forecast_temp_current": fore_temp,
                "current_temp_destination": curr_temp_dest,
                "forecast_temp_destination": fore_temp_dest,
                "decision": decision,
            },
            status=status.HTTP_200_OK,
        )

# Interface Segregation Principle (ISP):
# No interfaces to implement here.

# Dependency Inversion Principle (DIP):
# High-level modules should not depend on low-level modules, both should depend on abstractions.
