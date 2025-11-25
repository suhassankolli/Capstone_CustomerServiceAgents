from text_to_cypher_agent import TextToCypherAgent
from cohort_agent_client import CohortAgentClient
from summarization_agent_client import SummarizationAgentClient
from neo4j_memory import Neo4jMemoryStore

text_to_cypher_agent = TextToCypherAgent()

t2c_result = text_to_cypher_agent.query("What products does customer CUST0080 has with us")

print("------------ results ----------------")
print(t2c_result)