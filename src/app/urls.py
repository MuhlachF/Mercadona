from django.conf.urls.static import static
from django.urls import path
from app.views import AppHome
from Mercadona import settings
app_name = "app"

urlpatterns = [
    path('', AppHome.as_view(), name="home")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
