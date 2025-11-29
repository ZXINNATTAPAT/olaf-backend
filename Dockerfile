# Use Python 3.10 base image
FROM python:3.10-slim

# Install Rust and Cargo (required for Django-Bolt)
# Also install git (required for pip install from GitHub)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && rm -rf /var/lib/apt/lists/*

# Add Rust to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE $PORT

# Run migrations and start server
# Use sh -c to properly handle environment variables
CMD sh -c "python manage.py migrate --noinput && gunicorn mysite.wsgi --bind 0.0.0.0:\$PORT --workers 2 --timeout 120"

