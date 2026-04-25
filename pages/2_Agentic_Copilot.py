import streamlit as st
from services.agentic_broker import SupplyChainAgent

st.set_page_config(page_title="AI Agentic Broker", page_icon="🤖", layout="wide")

st.title("🤖 Autonomous Agentic Broker")
st.markdown("""
**Stochastic Negotiation Layer:** Describe a supply chain disruption in plain English. 
The Gemini AI agent will parse the context, determine the required capacity, and automatically route a strict JSON payload to the deterministic execution engine.
""")


@st.cache_resource
def get_agent():
    return SupplyChainAgent()


agent = get_agent()

disruption_text = st.text_area(
    "Describe the Disruption Event",
    value="Port strike in Rotterdam just halted our maritime freight. We urgently need to secure 12 containers via our RPA legacy carriers before prices spike.",
    height=150
)

if st.button("Deploy Autonomous Agent", type="primary"):
    with st.spinner("Agent is reasoning and negotiating via Gemini..."):
        success = agent.resolve_disruption(disruption_text)

        if success:
            st.success(
                "Mission Accomplished: Agent successfully translated the disruption into a deterministic webhook and fired it!")
            st.balloons()
        else:
            st.error("Agent execution failed. Check the terminal logs for hallucination or network errors.")
