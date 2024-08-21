from django.urls import path
from .views import DistrictListView
from .views import CoolestDistrictsAPIView
from .views import TemperatureComparisonAPIView

urlpatterns = [
    path('districts/', DistrictListView.as_view(), name='district-list'),
    path('coolest-districts/', CoolestDistrictsAPIView.as_view(), name='coolest-districts'),
    path('api/temperature-comparison/', TemperatureComparisonAPIView.as_view(), name='temperature-comparison'),
]
