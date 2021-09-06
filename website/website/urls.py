from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.contrib import admin

import os

urlpatterns = [
  path('', include('www.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if os.getenv('DEBUG', False):
  urlpatterns.append(path('site-admin/', admin.site.urls))