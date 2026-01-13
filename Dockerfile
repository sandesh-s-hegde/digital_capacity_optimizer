# 1. Use a lightweight Python version
FROM python:3.11-slim

# 2. Set the working folder
WORKDIR /app

# 3. Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your application code
COPY . .

# 5. The "Magic" Start Command
# This runs the migration script FIRST, then starts the website.
CMD sh -c "python migrate_csv_to_sql.py && streamlit run app.py --server.port $PORT --server.address 0.0.0.0"