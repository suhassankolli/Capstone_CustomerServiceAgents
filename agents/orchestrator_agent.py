from agents.sub_agents.text_to_cypher_agent import TextToCypherAgent
from agents.sub_agents.cohort_agent import CohortAgent
from agents.sub_agents.summary_agent import SummarizationAgent
from agents.graph.neo4j_memory import Neo4jMemoryStore


class OrchestratorAgent:
    """Business Accelerator / Orchestrator agent.

    Flow:
      1. Receive NL query.
      2. Call TextToCypher agent (Neo4j).
      3. Call Find Cohort agent (Google ADK via A2A).
      4. Call Summarization agent (Google ADK via A2A).
      5. Store conversation turns in Neo4j memory.
    """

    def __init__(
        self,
        memory_store: Neo4jMemoryStore | None = None,
        text_to_cypher_agent: TextToCypherAgent | None = None,
        cohort_agent: CohortAgent | None = None,
        summarizer: SummarizationAgent | None = None,
    ):
        self.memory = memory_store or Neo4jMemoryStore()
        self.text_to_cypher_agent = text_to_cypher_agent or TextToCypherAgent()
        self.cohort_agent = cohort_agent or CohortAgent()
        self.summarizer = summarizer or SummarizationAgent()

    def handle_query(
        self,
        session_id: str,
        query: str,
        customer_id: str | None = None,
    ) -> dict:
        # 1. log user query in memory
        self.memory.append_turn(
            session_id=session_id,
            role="user",
            text=query,
            customer_id=customer_id,
        )

        # 2. fetch recent context (for summarization)
        context = self.memory.get_recent_context(session_id, limit=10)

        # 3. call Text-to-Cypher agent
        t2c_result = self.text_to_cypher_agent.query(query+ f". for  Customer id {customer_id} ")

        # 4. call cohort agent
        cohort_result = self.cohort_agent.find_cohorts(
            query=query,
            customer_id=customer_id,
        )

        #print('-------- Query ----------\n')
        #print(query)
        #print('-------- End Query ----------\n')
        # 5. call summarization agent
        final_answer = self.summarizer.summarize(
            original_query=query,
            text_to_cypher_result=t2c_result,
            cohort_result=cohort_result,
            conversation_context=context,
        )

        # 6. store assistant response in memory
        self.memory.append_turn(
            session_id=session_id,
            role="assistant",
            text=final_answer,
            customer_id=customer_id,
        )

        return {
            "answer": final_answer,
            "text_to_cypher": t2c_result,
            "cohort": cohort_result,
        }
