FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    nginx \
    sqlite3 \
    nmap \
    whois \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create required directories
RUN mkdir -p /app/data /app/uploads

# Flag is passed via environment variable FLAG_UPLOAD in docker-compose.yml
# Student must achieve code execution to read it (env/printenv command)

# Nginx config
COPY nginx.conf /etc/nginx/sites-available/default

# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
