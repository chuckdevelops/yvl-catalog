#!/usr/bin/env python
"""
A very minimal Django application to verify Django is working correctly.
This skips the regular project structure and creates a standalone Django app.
"""

import sys
import os
from django.conf import settings
from django.core.management import execute_from_command_line
from django.http import HttpResponse
from django.urls import path

# Configure settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='simple-test-key',
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ],
        ALLOWED_HOSTS=['*'],
    )

# A simple view
def home(request):
    return HttpResponse(
        "Django is working! This is a basic test page."
    )

# URL patterns
urlpatterns = [
    path('', home),
]

# Run the application
if __name__ == '__main__':
    execute_from_command_line(sys.argv)