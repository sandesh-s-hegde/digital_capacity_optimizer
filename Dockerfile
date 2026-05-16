# Base image optimized for minimal production footprint
FROM python:3.12-slim

# Enforce strict Python environment variables
# 1. Prevents Python from writing .pyc files to disk
# 2. Ensures stdout and stderr are streamed instantly to cloud logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the remaining application payload
COPY . .

# Execute Streamlit server bound to the dynamic cloud port
CMD sh -c "streamlit run Dashboard.py --server.port $PORT --server.address 0.0.0.0"
