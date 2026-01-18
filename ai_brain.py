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
        # Use the alias that points to the stable 1.5 Flash model
        return genai.GenerativeModel('models/gemini-flash-latest')
    except Exception as e:
        print(f"Error configuring model: {e}")
        return None


def analyze_supply_chain(df, metrics):
    """(Legacy) One-off report generation."""
    if not api_key:
        return "⚠️ **System Notice:** I need an API Key to think. Please check your settings."

    model = get_model()
    if not model:
        return "🔌 **Connection Error:** I couldn't reach the AI brain. Try again in a moment."

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
    Handles the chat conversation with strict guardrails.
    """
    if not api_key:
        return "⚠️ **System Notice:** I need an API Key to think. Please check your settings."

    model = get_model()
    if not model:
        return "🔌 **Connection Error:** I couldn't reach the AI brain. Try again in a moment."

    try:
        # 1. Build the "System Prompt" with GUARDRAILS
        # We explicitly tell it what NOT to do.
        system_instruction = f"""
        You are a specialized Supply Chain Assistant named 'CapOpt'. 

        YOUR CONTEXT (Real-Time Data):
        - Avg Monthly Demand: {metrics['avg_demand']} units
        - Volatility (Std Dev): {metrics['std_dev']} units
        - EOQ (Optimal Order): {metrics['eoq']} units
        - Simulated Safety Stock: {metrics['safety_stock']} units
        - Simulated Service Level: {metrics['sla'] * 100:.1f}%

        YOUR MISSION:
        1. Analyze inventory risks based STRICTLY on the data above.
        2. Explain technical terms (like EOQ or Safety Stock) simply.
        3. If the user changes the Service Level slider, explain the trade-off (higher service = higher cost/stock).

        GUARDRAILS (CRITICAL):
        - DO NOT answer questions unrelated to supply chain, inventory, business, or math.
        - If asked about general topics (e.g., "Capital of France", "Write a poem", "Politics"), politely refuse: "I am tuned only for supply chain analytics."
        - DO NOT attempt complex math predictions yourself. Rely on the metrics provided above.
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