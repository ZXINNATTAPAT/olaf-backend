# Django-Bolt APIs are integrated via APIView in Django URLs
# Use standard Django deployment with gunicorn
# Note: Migrations and collectstatic are handled by Railway's release phase
# or can be run manually after deployment
web: gunicorn mysite.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 50
