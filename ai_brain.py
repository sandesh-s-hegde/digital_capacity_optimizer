import os
import google.generativeai as genai
import streamlit as st

api_key = os.getenv("GEMINI_API_KEY")


def analyze_supply_chain(df, metrics):
    if not api_key:
        return "❌ Error: API Key missing."

    try:
        genai.configure(api_key=api_key)

        # CHANGED: 'gemini-flash-latest' points to the stable version
        # (usually 1.5 Flash) which has the best Free Tier availability.
        model = genai.GenerativeModel('models/gemini-flash-latest')

        context = f"""
        You are a Supply Chain expert.
        DATA:
        - Demand History: {df.tail(5)['demand'].tolist()}
        - Avg Demand: {metrics['avg_demand']}
        - EOQ: {metrics['eoq']}
        - Safety Stock: {metrics['safety_stock']}

        Write a 3-bullet executive summary on inventory risks.
        """

        response = model.generate_content(context)
        return response.text

    except Exception as e:
        return f"❌ AI Error: {str(e)}"