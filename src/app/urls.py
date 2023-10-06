from django.conf.urls.static import static
from django.urls import path
from app.views import AppHome
from app import views
from Mercadona import settings
app_name = "app"

urlpatterns = [
    path('', AppHome.as_view(), name="home"),
    path('api/get_articles/', views.get_articles, name='get_articles')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
