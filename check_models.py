import google.generativeai as genai
import os

# Get the key (make sure you set it in the terminal first!)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: API Key not found in environment variables.")
else:
    try:
        genai.configure(api_key=api_key)
        print("🔍 Checking available models for your key...")
        print("------------------------------------------------")

        found_any = False
        for m in genai.list_models():
            # We only care about models that can write text (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Available: {m.name}")
                found_any = True

        if not found_any:
            print("⚠️ No text generation models found. Check your API Key permissions.")

    except Exception as e:
        print(f"❌ Connection Error: {e}")