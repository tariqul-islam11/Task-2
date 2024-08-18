from django.urls import path
from .views import CoolestDistrictsAPIView
from .views import DistrictListView

urlpatterns = [
    path('coolest-districts/', CoolestDistrictsAPIView.as_view(), name='coolest-districts'),
    path('api/districts/', DistrictListView.as_view(), name='district-list'),
]