import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def chat_with_data(user_query, chat_history, df, metrics):
    """
    Interfaces with the Gemini API to provide contextual supply chain analysis.
    Implements exponential backoff for rate limit (429) handling.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: Missing GEMINI_API_KEY in environment."

    try:
        genai.configure(api_key=api_key)

        uc = metrics.get('unit_cost', 50)
        sp = metrics.get('selling_price', 85)
        h_cost = metrics.get('holding_cost', 10)
        margin = sp - uc

        optimal_sla = margin / (margin + h_cost) if (margin + h_cost) > 0 else 0.95
        total_space = metrics.get('avg_demand', 0) + metrics.get('safety_stock', 0)
        outsourced_vol = metrics.get('outsourced', 0)

        data_context = f"""
        [LSP DIGITAL TWIN STATE]
        Transport Mode: {metrics.get('transport_mode', 'Road')}
        Warehouse Capacity: 150 units

        [OPERATIONAL METRICS]
        Average Demand: {metrics.get('avg_demand', 0)} units
        Safety Stock: {metrics.get('safety_stock', 0)} units
        Total Capacity Used: {total_space} units
        Outsourced Volume: {outsourced_vol} units
        Cooperation Status: {"ACTIVE" if outsourced_vol > 0 else "INTERNAL"}

        [FINANCIAL METRICS]
        Unit Cost: USD {uc} | Selling Price: USD {sp} | Margin: USD {margin}
        Holding Cost: USD {h_cost}/unit
        Optimal SLA (Newsvendor): {optimal_sla:.1%}

        [STRATEGIC METRICS]
        Resilience Score: {metrics.get('resilience_score', 'N/A')}/100
        CO2 Emissions: {metrics.get('co2_emissions', 0)} kg
        Customer Loyalty: {metrics.get('loyalty_score', 0)}/100
        """

        system_instruction = """
        You are a quantitative research assistant for a Logistics Service Provider.

        Formatting constraints (Streamlit environment):
        - Never use unescaped '$' signs for currency, as it breaks the UI rendering. Use 'USD' or escape it as '\$'.
        - Use standard markdown for lists and emphasis.
        - Only use standard LaTeX notation for complex mathematical formulas (e.g., $$ Cu = SP - UC $$).

        Behavioral constraints:
        - Limit responses strictly to supply chain, operations research, and financial risk topics.
        - Ground all strategic advice in the provided numerical context (Newsvendor logic, margins, risk scores).
        - Maintain a concise, academic, and highly professional tone.
        """

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )

        clean_history = [
            {"role": "user" if msg['role'] == 'user' else "model", "parts": msg['parts']}
            for msg in (chat_history[-4:] if chat_history else [])
            if msg.get('parts')
        ]

        chat = model.start_chat(history=clean_history)
        prompt = f"{data_context}\n\nUSER QUESTION: {user_query}"

        for attempt in range(3):
            try:
                response = chat.send_message(prompt)
                return response.text
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "quota" in error_msg:
                    if attempt < 2:
                        time.sleep(5 * (attempt + 1))  # Exponential backoff
                        continue
                    return "Traffic limit reached. Please wait a moment and try again."
                return f"Model execution error: {str(e)}"

    except Exception as e:
        return f"System error: {str(e)}"
