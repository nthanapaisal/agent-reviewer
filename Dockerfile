FROM python:3.11-slim

# Install ffmpeg and build tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (to leverage Docker cache)
COPY requirements.txt .

# Upgrade pip and install wheel to support packages using setup.py
RUN pip install --upgrade pip wheel setuptools

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["/bin/bash", "-c", "PYTHONPATH=./backend uvicorn main:app --host 0.0.0.0 --reload"]
