FROM python:3.11-bookworm

# Install ffmpeg and any dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Run the application using uvicorn
CMD ["/bin/bash", "-c", "PYTHONPATH=./src uvicorn main:app --host 0.0.0.0 --reload"]
