from django.contrib import admin
from django.urls import path, include

import os

urlpatterns = [
  path('', include('www.urls'))
]

if os.getenv('DEBUG', False):
  urlpatterns.append(path('site-admin/', admin.site.urls))