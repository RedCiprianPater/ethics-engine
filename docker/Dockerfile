# Ethics Engine Docker Image

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml .
COPY README.md .

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[api]"

# Copy application code
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV ETHICS_ENGINE_ENV=production

# Expose port
EXPOSE 8000

# Run the API server
CMD ["uvicorn", "ethics_engine.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
