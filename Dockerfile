FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for scipy/numpy, psycopg2, and weasyprint
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-xlib-2.0-0 libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command, overridden in docker-compose.yml
CMD ["uvicorn", "services.api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
