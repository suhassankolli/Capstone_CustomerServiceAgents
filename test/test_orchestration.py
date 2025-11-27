from agents.orchestrator_agent import OrchestratorAgent

objOrchestratorAgent  = OrchestratorAgent()
result = objOrchestratorAgent.handle_query(session_id="sess_CUST0002",
                                           query="What products does customer CUST0002 has with us",
                                           customer_id="CUST0002")

print("--- Results ---")
print(result)