# 1. Base Image: Use a lightweight Linux with Python 3.11 pre-installed
FROM python:3.11-slim

# 2. Setup: Create a folder named 'app' inside the container
WORKDIR /app

# 3. Dependencies: Copy the requirements file and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Code: Copy all your project files into the container
COPY . .

# ... (Previous lines same as before)

# 5. Network: Open port 8501 (Streamlit's default port)
EXPOSE 8501

# 6. Startup:
# We use the shell form to allow variable expansion if needed,
# but for now, we will stick to 8501 and configure the cloud to match us.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]