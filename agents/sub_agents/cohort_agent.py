from config import COHORT_AGENT_ID, GCP_PROJECT_ID, GCP_LOCATION
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from .text_to_cypher_agent import TextToCypherAgent

class CohortAgent:
    """Client wrapper for Google ADK 'Find Cohorts' agent, via A2A.

    Replace `_call_adk_agent` with your real A2A implementation.
    """

    def __init__(self):
        self.agent_id = COHORT_AGENT_ID
        self.project_id = GCP_PROJECT_ID
        self.location = GCP_LOCATION

    def _call_adk_agent(self, query: str, customer_id: str | None) -> dict:
        # TODO: Implement the actual call to Google ADK / Vertex AI Agents.
        # This is a stub that returns a plausible payload shape.
        text_to_cypher_agent = TextToCypherAgent()
        t2c_result = text_to_cypher_agent.query(f"Can you find all Open events that is assocoated with the customer {customer_id}")
        return t2c_result
        
    def find_cohorts(self, query: str, customer_id: str | None = None) -> dict:
        return self._call_adk_agent(query=query, customer_id=customer_id)
