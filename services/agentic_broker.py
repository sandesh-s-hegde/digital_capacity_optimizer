import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from services.dispatcher import EcosystemDispatcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] AgenticBroker: %(message)s")
logger = logging.getLogger("AgenticBroker")

load_dotenv()


class SupplyChainAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.dispatcher = EcosystemDispatcher()

        self.system_prompt = """
        You are an autonomous supply chain procurement agent. 
        Your job is to read supply chain disruptions and output a strict JSON payload to procure backup capacity.

        The JSON must perfectly match this schema:
        {
            "Target Ecosystem Route": "Modern B2B (API)" OR "Legacy Carrier (RPA)",
            "Assets to Procure": <integer>,
            "Reason": "<brief summary of the disruption>"
        }
        """

    def resolve_disruption(self, natural_language_prompt: str) -> bool:
        logger.info("Agent received stochastic disruption event. Reasoning with Gemini...")

        try:
            response = self.model.generate_content(
                f"{self.system_prompt}\n\nDisruption Event: {natural_language_prompt}",
                generation_config=genai.GenerationConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                )
            )

            payload = json.loads(response.text)
            logger.info(f"Agent successfully generated payload: {json.dumps(payload)}")

            logger.info("Handing execution to the Ecosystem Dispatcher...")
            return self.dispatcher.dispatch_sync(payload)

        except json.JSONDecodeError:
            logger.error(f"Agent Hallucination Error: Output was not valid JSON. Raw output: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Agent Execution Failure: {str(e)}")
            return False


if __name__ == "__main__":
    agent = SupplyChainAgent()
    disruption = "Port strike in Rotterdam just halted our maritime freight. We urgently need to secure 12 containers via our RPA legacy carriers before prices spike."
    agent.resolve_disruption(disruption)
