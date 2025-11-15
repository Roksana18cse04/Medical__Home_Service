# Use Python 3.12 slim image as base
FROM python:3.12.1-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    libsamplerate0 \
    libsamplerate0-dev \
    portaudio19-dev \
    libasound2 \
    libasound2-dev \
    alsa-utils \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libatlas3-base \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*



# Copy dependency list
COPY requirements.txt .

# Install Python dependencies via uv
RUN  pip install --system -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Optional healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/docs')" || exit 1

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
