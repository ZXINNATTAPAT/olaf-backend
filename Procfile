# Django-Bolt APIs are integrated via APIView in Django URLs
# Use standard Django deployment with gunicorn
# Note: When using Dockerfile, Railway uses Dockerfile CMD instead of Procfile
# This Procfile is kept for reference but Dockerfile CMD takes precedence
# Release command runs migrations and collects static files (runs after build)
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: gunicorn mysite.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 50
