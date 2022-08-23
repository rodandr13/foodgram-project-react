from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    #path('users/', include('users.urls', namespace='users')),
    #path('recipes/', include('users.urls', namespace='users')),
]
