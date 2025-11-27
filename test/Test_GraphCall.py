from agents.sub_agents.text_to_cypher_agent import TextToCypherAgent
from agents.sub_agents.cohort_agent import CohortAgent
from agents.sub_agents.summary_agent import SummarizationAgent
from agents.graph.neo4j_memory import Neo4jMemoryStore

text_to_cypher_agent = TextToCypherAgent()

t2c_result = text_to_cypher_agent.query("What products does customer CUST0080 has with us")

print("------------ results ----------------")
print(t2c_result)