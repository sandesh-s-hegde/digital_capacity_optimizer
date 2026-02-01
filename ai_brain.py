import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def chat_with_data(user_query, chat_history, df, metrics):
    """
    Sends the user query + rigorous data context to Gemini.
    Includes financial logic to interpret Heatmaps and Profitability.
    """

    # 1. SETUP API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Error: Missing GEMINI_API_KEY. Please check your .env file."

    try:
        genai.configure(api_key=api_key)

        # 2. CALCULATE LOGIC (THE "READING" PART)
        total_space_needed = metrics['avg_demand'] + metrics['safety_stock']
        warehouse_cap = 150
        is_outsourcing = metrics.get('outsourced', 0) > 0

        # Financial Math (Reading the Heatmap)
        uc = metrics.get('unit_cost', 50)
        sp = metrics.get('selling_price', 85)
        h_cost = metrics.get('holding_cost', 10)
        margin = sp - uc

        # The Critical Ratio (Newsvendor Optimal Point) - The "Peak" of the Heatmap
        # Formula: Margin / (Margin + Holding Cost)
        if (margin + h_cost) > 0:
            optimal_sla_math = margin / (margin + h_cost)
        else:
            optimal_sla_math = 0.95

        # 3. CONSTRUCT THE CONTEXT BLOCK
        data_context = f"""
        [LSP DIGITAL TWIN DATA STREAM]

        --- OPERATIONAL METRICS ---
        1. Average Demand: {metrics['avg_demand']} units
        2. Safety Stock: {metrics['safety_stock']} units
        3. Total Capacity Used: {total_space_needed} units
        4. Outsourced Volume: {metrics.get('outsourced', 0)} units (Status: {"COOPERATION ACTIVE" if is_outsourcing else "INTERNAL"})

        --- FINANCIAL METRICS (HEATMAP DATA) ---
        1. Unit Cost: ${uc} | Selling Price: ${sp} | Margin: ${margin}
        2. Holding Cost: ${h_cost}/unit
        3. HEATMAP INSIGHT: Based on these costs, the "Sweet Spot" (Maximum Profit) is at a Service Level of {optimal_sla_math:.1%}.
           - If SLA < {optimal_sla_math:.1%}: You lose money from Stockouts (Lost Sales).
           - If SLA > {optimal_sla_math:.1%}: You lose money from Excess Inventory (Holding Costs).

        --- RESILIENCE ---
        - Resilience Score: {metrics.get('resilience_score', 'N/A')}/100
        """

        # 4. SYSTEM INSTRUCTIONS
        system_instruction = """
                You are a specialized Research Assistant for a Logistics Service Provider.

                ### STRICT RULES:
                1. **SCOPE:** Refuse questions about capitals, weather, or non-logistics topics.
                2. **ACCURACY:** If the user asks "What does the heatmap say?", use the [FINANCIAL METRICS] section above. Explain that the heatmap shows the trade-off between risk and cost.
                3. **DIAGRAMS:** When explaining concepts, use these EXACT markdown links to show diagrams:
                   - If explaining the "Sweet Spot", "Optimal SLA", or "Newsvendor Model": 
                     Display this image: 
                     ![Normal Distribution](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Standard_deviation_diagram.svg/640px-Standard_deviation_diagram.svg.png)

                   - If explaining "Cost Trade-offs" or "EOQ": 
                     Display this image:
                     ![Cost Curve](https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Economic_Order_Quantity_pdf.svg/640px-Economic_Order_Quantity_pdf.svg.png)

                4. **TONE:** Professional, Concise.
                """

        # 5. INITIALIZE MODEL
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=system_instruction
        )

        # 6. HISTORY & SEND
        clean_history = []
        for msg in chat_history[-4:]:
            role = "user" if msg['role'] == 'user' else "model"
            clean_history.append({"role": role, "parts": [msg['parts'][0]]})

        # --- THE FIX IS HERE ---
        chat = model.start_chat(history=clean_history)
        # -----------------------

        full_prompt = f"{data_context}\n\nUSER QUESTION: {user_query}"

        response = chat.send_message(full_prompt)
        return response.text

    except Exception as e:
        return f"❌ AI Error: {str(e)}"