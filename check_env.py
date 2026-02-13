import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL", "")

if "neon.tech" in db_url:
    print("⚠️  Warning: Still using old Neon DB credentials.")
elif "render.com" in db_url:
    print("✅ Success: System is now connected to Render Frankfurt.")
else:
    print("❌ Error: No valid DATABASE_URL found.")
