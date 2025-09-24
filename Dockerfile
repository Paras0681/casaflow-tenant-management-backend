# ------------------------------
# 1. Base image
# ------------------------------
FROM python:3.11-slim

# ------------------------------
# 2. Set work directory
# ------------------------------
WORKDIR /app

# ------------------------------
# 3. Set environment variables for Python
# ------------------------------
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ------------------------------
# 4. Install system dependencies
# ------------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------
# 5. Install Python dependencies
# ------------------------------
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# ------------------------------
# 6. Copy project files
# ------------------------------
COPY tenant-management/ /app/

# ------------------------------
# 7. Expose port
# ------------------------------
EXPOSE 8000

# ------------------------------
# 8. Entrypoint
#    This will:
#    1. Collect static files
#    2. Run migrations
#    3. Start Gunicorn
# ------------------------------
ENTRYPOINT ["sh", "-c", "\
    echo 'Running collectstatic...' && \
    python manage.py collectstatic --noinput && \
    echo 'Running migrations...' && \
    python manage.py migrate && \
    echo 'Starting Gunicorn...' && \
    gunicorn tenant_management.wsgi:application --bind 0.0.0.0:8000 \
"]
