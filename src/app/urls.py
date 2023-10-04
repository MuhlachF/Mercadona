from django.urls import path
from app.views import AppHome

app_name = "app"

urlpatterns = [
    path('', AppHome.as_view(), name="home")
]
