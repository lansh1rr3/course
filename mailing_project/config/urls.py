from django.contrib import admin
from django.urls import path, include
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mailing.urls')),
    path('users/', include('users.urls')),
]
