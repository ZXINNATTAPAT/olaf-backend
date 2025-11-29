"""
Run Django-Bolt server.
Django-Bolt integrates with Django through APIView in URLs.
Use Django's runserver or gunicorn with Bolt APIs mounted via APIView.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Note: Django-Bolt APIs are mounted via APIView in mysite/urls.py
# To run with Bolt APIs, uncomment bolt_urls in mysite/urls.py
# Then use: python manage.py runserver

if __name__ == '__main__':
    print("Django-Bolt APIs are integrated via APIView in Django URLs.")
    print("To use Bolt APIs:")
    print("1. Uncomment bolt_urls in mysite/urls.py")
    print("2. Run: python manage.py runserver")
    print("\nOr use gunicorn:")
    print("gunicorn mysite.wsgi --bind 0.0.0.0:8000")

