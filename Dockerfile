FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x healthcheck.sh

EXPOSE 8080

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DB_HOST=l4w0wss00osgkkokkgc04cwk
ENV DB_PORT=3306
ENV DB_USER=mysql
ENV DB_PASSWORD=Finonest@112233
ENV DB_NAME=default
ENV DATABASE_URL=mysql://mysql:Finonest%40112233@l4w0wss00osgkkokkgc04cwk:3306/default

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD ["./healthcheck.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "api_server:app"]
