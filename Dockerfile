FROM python:3.11-slim

# Install system dependencies required for OpenCV, Mediapipe, pyaudio, and espeak
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libasound2-dev \
    portaudio19-dev \
    libgl1 \
    libglib2.0-0 \
    espeak \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose the FastAPI dashboard port
EXPOSE 8000

# Set environment variables
ENV OLLAMA_API_URL=http://ollama-service:11434/api/chat
ENV OLLAMA_HOST=http://ollama-service:11434

# Start the dashboard server
CMD ["python", "CHAOS.py"]
