import os
import google.generativeai as genai
import streamlit as st

# 1. Get the Key
api_key = os.getenv("GEMINI_API_KEY")

# 2. Configure Globally if key exists
if api_key:
    genai.configure(api_key=api_key)


def get_model():
    """Returns the configured generative model."""
    if not api_key:
        return None
    try:
        # Use the alias that worked for you
        return genai.GenerativeModel('models/gemini-flash-latest')
    except Exception as e:
        print(f"Error configuring model: {e}")
        return None


def analyze_supply_chain(df, metrics):
    """(Legacy) One-off report generation."""
    if not api_key: return "⚠️ Error: API Key missing. Please set GEMINI_API_KEY in your terminal."

    model = get_model()
    if not model: return "❌ AI Error: Could not load model."

    context = f"""
    You are a Supply Chain expert.
    DATA SUMMARY:
    - Recent Demand: {df.tail(5)['demand'].tolist()}
    - Avg Demand: {metrics['avg_demand']}
    - EOQ: {metrics['eoq']}
    - Safety Stock: {metrics['safety_stock']}

    Task: Write a 3-bullet executive summary on inventory risks.
    """
    response = model.generate_content(context)
    return response.text


def chat_with_data(user_message, history, df, metrics):
    """
    Handles the chat conversation with error safety.
    """
    # CRITICAL CHECK: Stop before crashing if no key
    if not api_key:
        return "⚠️ System Error: API Key is missing. Please set GEMINI_API_KEY in your environment."

    model = get_model()
    if not model: return "❌ Error: AI Brain not connected."

    try:
        # 1. Build the "System Prompt"
        system_instruction = f"""
        You are a specialized Supply Chain Assistant. 
        You have access to the following REAL-TIME data:

        - Average Monthly Demand: {metrics['avg_demand']} units
        - Standard Deviation (Volatility): {metrics['std_dev']} units
        - Optimal Order Quantity (EOQ): {metrics['eoq']} units
        - Safety Stock: {metrics['safety_stock']} units
        - Latest Data Points: {df.tail(5)['demand'].tolist()}

        RULES:
        1. Answer strictly based on this data.
        2. Keep answers short, professional, and helpful.
        """

        # 2. Start the Chat Session with History
        chat = model.start_chat(history=history)

        # 3. Handle First Message vs Follow-ups
        if not history:
            full_prompt = f"{system_instruction}\n\nUSER QUESTION: {user_message}"
        else:
            full_prompt = user_message

        response = chat.send_message(full_prompt)
        return response.text

    except Exception as e:
        return f"❌ AI Error: {str(e)}"