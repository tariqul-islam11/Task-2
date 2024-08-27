from django.urls import path
from .views import CoolestDistrictsAPIView
from .views import TemperatureComparisonAPIView

urlpatterns = [
    path('coolest-districts/', CoolestDistrictsAPIView.as_view(), name='coolest-districts'),
    path('api/temperature-comparison/', TemperatureComparisonAPIView.as_view(), name='temperature-comparison'),
]
