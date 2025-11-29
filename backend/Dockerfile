FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install uv && uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x /app/scripts/entrypoint.sh /app/scripts/init_db.sh

# Expose port
EXPOSE 8009

# Use entrypoint script
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
