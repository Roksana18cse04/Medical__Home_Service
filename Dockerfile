# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies
# Required for: audio processing (librosa, sounddevice, pydub), ffmpeg, ML libs (faiss, tensorflow)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    libsamplerate0 \
    libsamplerate0-dev \
    portaudio19-dev \
    alsa-lib \
    alsa-utils \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package installer)
RUN pip install --upgrade pip uv

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies using uv (faster than pip)
RUN uv pip install --system -r requirements.txt



# Copy application code
COPY . .

# Expose port for FastAPI (default 8000)
EXPOSE 8000

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/docs')" || exit 1

# Command to run FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
