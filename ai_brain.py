import os
import google.generativeai as genai
import pandas as pd


def chat_with_data(user_query, chat_history, df, metrics):
    """
    Sends the user's question + the relevant data to Gemini.
    """
    # 1. SETUP API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Error: Missing GEMINI_API_KEY. Please check your .env file or Render settings."

    try:
        genai.configure(api_key=api_key)

        # 2. PREPARE DATA CONTEXT
        if df is not None and not df.empty:
            # Get last 5 months of data to see the trend
            recent_data = df.tail(5).to_string(index=False)
            data_context = f"""
            Recent Data History:
            {recent_data}

            Key Metrics:
            - Product: {metrics.get('product_name', 'Unknown')}
            - Avg Demand: {metrics.get('avg_demand', 0)} units
            - Safety Stock: {metrics.get('safety_stock', 0)} units
            - Recommended Order (EOQ): {metrics.get('eoq', 0)} units
            - Current SLA Target: {metrics.get('sla', 0.95) * 100}%
            - Lead Time: {metrics.get('lead_time', 1)} months
            """
        else:
            data_context = "No data available in the database yet."

        # 3. BUILD THE SYSTEM PROMPT
        system_instruction = f"""
        You are a Supply Chain expert analyzing inventory data.

        CONTEXT:
        {data_context}

        RULES:
        1. Answer ONLY based on the data provided above. 
        2. Do NOT talk about stock markets, weather, or generic business advice.
        3. If the user asks why the forecast is down, look at the 'Recent Data History'. If the numbers are dropping (e.g., 150 -> 120 -> 100), say "The trend is downward based on recent sales."
        4. Keep answers short (max 3 sentences) and professional.
        """

        # 4. SEND TO GOOGLE
        # FIX: Using 'gemini-flash-latest' points to the best stable model for your tier
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=system_instruction
        )

        # Format history for Gemini
        clean_history = []
        for msg in chat_history[-4:]:  # Keep only last 4 messages
            role = "user" if msg['role'] == 'user' else "model"
            clean_history.append({"role": role, "parts": [msg['parts'][0]]})

        chat = model.start_chat(history=clean_history)
        response = chat.send_message(user_query)

        return response.text

    except Exception as e:
        return f"❌ AI Error: {str(e)}"