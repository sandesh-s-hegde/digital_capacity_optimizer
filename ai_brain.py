import os
import google.generativeai as genai
import streamlit as st

# Configure the API
# We try to get the key from Environment (Render) or Streamlit Secrets (Local)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # Fallback for local testing if env var isn't set
    # ideally, use st.secrets or set the env var in your terminal
    print("⚠️ Warning: GEMINI_API_KEY not found.")


def analyze_supply_chain(df, metrics):
    """
    Sends the data summary to Gemini and gets a strategic report.
    """
    if not api_key:
        return "❌ Error: API Key missing. Please set GEMINI_API_KEY."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 1. Prepare the Data Context (The Prompt Engineering)
        # We turn the raw numbers into a story for the AI.
        context = f"""
        You are a Supply Chain expert analyzing inventory data.

        DATA SUMMARY:
        - Recent Demand History (Last 5 entries): {df.tail(5)['demand'].tolist()}
        - Average Monthly Demand: {metrics['avg_demand']}
        - Recommended Order (EOQ): {metrics['eoq']}
        - Required Safety Stock: {metrics['safety_stock']}
        - Current Volatility (Std Dev): {metrics['std_dev']}

        TASK:
        Write a concise, executive summary (3-4 bullet points).
        1. Identify if the demand is stable or volatile.
        2. Explain WHY we need the recommended safety stock.
        3. Recommend a specific action for the procurement manager.

        Keep it professional but urgent. Use emojis where appropriate.
        """

        # 2. Call the AI
        response = model.generate_content(context)

        # 3. Return the text
        return response.text

    except Exception as e:
        return f"❌ AI Error: {str(e)}"