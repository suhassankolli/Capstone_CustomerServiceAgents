import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j connection
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://<host>:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# LLM configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Google ADK / A2A configuration (replace with your real values)
COHORT_AGENT_ID = os.getenv("COHORT_AGENT_ID", "find-cohort-agent")
SUMMARIZATION_AGENT_ID = os.getenv("SUMMARIZATION_AGENT_ID", "summarization-agent")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "my-project")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
