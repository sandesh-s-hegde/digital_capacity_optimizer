import os
import db_manager


def run_diagnostics():
    print("🩺 LSP Digital Twin: Running Health Check...")
    # Check Environment
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"AI Gateway: {'✅ Ready' if api_key else '❌ Missing API Key'}")

    # Check Database
    try:
        db_manager.init_db()
        print("Database Status: ✅ Connected")
    except Exception as e:
        print(f"Database Status: ❌ Error: {e}")


if __name__ == "__main__":
    run_diagnostics()
