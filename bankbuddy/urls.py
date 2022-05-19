
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('', include('authsystem.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
]
