"""
Django-Bolt URL configuration.
This integrates Django-Bolt API routes with Django's URL system.
"""
from django.urls import path, include
from django_bolt import APIView
from blog import bolt_api as blog_api
from authentication import bolt_api as auth_api

# Mount Bolt APIs using APIView
urlpatterns = [
    # Mount blog API at /api/
    path('api/', APIView(blog_api.api)),
    # Mount auth API at /api/auth/
    path('api/auth/', APIView(auth_api.api)),
]

