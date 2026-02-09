import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def chat_with_data(user_query, chat_history, df, metrics):
    """
    Sends the user query to Gemini with automatic Retry logic
    to handle '429 Quota Exceeded' errors gracefully.
    """

    # 1. SETUP API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Error: Missing GEMINI_API_KEY. Please check your .env file."

    try:
        genai.configure(api_key=api_key)

        # 2. CONTEXT LOGIC
        total_space_needed = metrics['avg_demand'] + metrics['safety_stock']
        warehouse_cap = 150
        is_outsourcing = metrics.get('outsourced', 0) > 0
        transport_mode = metrics.get('transport_mode', 'Road')

        # Financial Math
        uc = metrics.get('unit_cost', 50)
        sp = metrics.get('selling_price', 85)
        h_cost = metrics.get('holding_cost', 10)
        margin = sp - uc

        if (margin + h_cost) > 0:
            optimal_sla_math = margin / (margin + h_cost)
        else:
            optimal_sla_math = 0.95

        # 3. BUILD CONTEXT STRING
        # We use 'USD' here to avoid confusing the AI, but instruct it to output '\$' later
        data_context = f"""
        [LSP DIGITAL TWIN DATA STREAM]

        --- CONFIGURATION ---
        Mode: {transport_mode}
        Warehouse Cap: {warehouse_cap} units

        --- OPERATIONAL METRICS ---
        1. Average Demand: {metrics['avg_demand']} units
        2. Safety Stock: {metrics['safety_stock']} units
        3. Total Capacity Used: {total_space_needed} units
        4. Outsourced Volume: {metrics.get('outsourced', 0)} units (Status: {"COOPERATION ACTIVE" if is_outsourcing else "INTERNAL"})

        --- FINANCIAL METRICS ---
        1. Unit Cost: USD {uc} | Selling Price: USD {sp} | Margin: USD {margin}
        2. Holding Cost: USD {h_cost}/unit
        3. OPTIMAL SLA (Newsvendor): {optimal_sla_math:.1%} (Based on Cost vs Risk)

        --- STRATEGIC METRICS ---
        1. Resilience Score: {metrics.get('resilience_score', 'N/A')}/100
        2. CO2 Emissions: {metrics.get('co2_emissions', 0)} kg
        3. Customer Loyalty: {metrics.get('loyalty_score', 0)}/100
        """

        # 4. SYSTEM INSTRUCTIONS (Fixed for Streamlit LaTeX Conflict)
        system_instruction = """
        You are a specialized Research Assistant for a Logistics Service Provider.

        ### CRITICAL STREAMLIT FORMATTING RULES:
        1. **CURRENCY ESCAPING:** Streamlit uses '$' for math formulas. You MUST escape dollar signs in text.
           - **WRONG:** "The cost is $50." (This triggers LaTeX mode and deletes spaces)
           - **RIGHT:** "The cost is \$50." (Use a backslash before every dollar sign)

        2. **SPACING:** Do not run numbers into text.
           - **WRONG:** "Margin(\$35)against"
           - **RIGHT:** "Margin (\$35) against"

        3. **MATH BLOCKS:** Only use standard LaTeX for actual formulas, not for simple currency.
           - Example: $$ Cu = SP - UC $$ is fine.
           - Example: "Profit is \$100" is fine.

        ### CONTENT RULES:
        1. **SCOPE:** Refuse questions about capitals, weather, or non-logistics topics.
        2. **ACCURACY:** If the user asks "What does the heatmap say?", explain the trade-off between risk and cost using the [FINANCIAL METRICS].
        3. **DIAGRAMS:** When explaining concepts, use these EXACT markdown links:
           - "Sweet Spot" / "Optimal SLA": 

           - "Cost Trade-offs" / "Cost Curve": 


        ### TONE:
        Professional, Concise, Research-Oriented.
        """

        # 5. INITIALIZE MODEL
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=system_instruction
        )

        # 6. BUILD HISTORY
        clean_history = []
        if chat_history:
            for msg in chat_history[-4:]:
                role = "user" if msg['role'] == 'user' else "model"
                if msg.get('parts'):
                    clean_history.append({"role": role, "parts": msg['parts']})

        chat = model.start_chat(history=clean_history)
        full_prompt = f"{data_context}\n\nUSER QUESTION: {user_query}"

        # 7. RETRY LOGIC
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = chat.send_message(full_prompt)
                return response.text
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "quota" in error_msg:
                    if attempt < max_retries - 1:
                        time.sleep(10)
                        continue
                    else:
                        return "⚠️ **Traffic Limit:** The AI is busy. Please wait 30 seconds."
                else:
                    return f"❌ AI Error: {str(e)}"

    except Exception as e:
        return f"❌ System Error: {str(e)}"