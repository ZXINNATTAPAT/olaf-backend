# Django-Bolt APIs are integrated via APIView in Django URLs
# Use standard Django deployment with gunicorn
# Release command runs migrations and conditionally collects static files
# Static files are disabled in production (ENABLE_STATIC_FILES=False) to reduce build size
# Note: Set ENABLE_STATIC_FILES=True in environment variables if you need static files
release: python manage.py migrate --noinput && (if [ "$ENABLE_STATIC_FILES" = "True" ]; then python manage.py collectstatic --noinput --clear --no-post-process; else echo "Static files disabled (ENABLE_STATIC_FILES=False)"; fi) || python manage.py migrate --noinput
web: gunicorn mysite.wsgi --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 50 --preload
