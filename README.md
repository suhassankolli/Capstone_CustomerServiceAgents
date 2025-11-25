# Customer Service Agentic Application (Neo4j + LLM + Google ADK stubs)

This project demonstrates an end-to-end **agentic** architecture for a
customer service assistant that works against your existing Neo4j graph.

Components:

- **Streamlit UI** (`app_streamlit.py`) – chat-style UX for customer service reps.
- **OrchestratorAgent** (`orchestrator_agent.py`) – Business Accelerator agent
  coordinating sub-agents.
- **TextToCypherAgent** (`text_to_cypher_agent.py`) – converts natural-language
  questions to Cypher using an LLM (LangChain + Neo4jGraph) and executes them.
- **CohortAgentClient** (`cohort_agent_client.py`) – stub client using A2A to call
  your Google ADK "Find Cohorts" agent.
- **SummarizationAgentClient** (`summarization_agent_client.py`) – stub client using
  A2A to call your Google ADK summarization agent.
- **Neo4jMemoryStore** (`neo4j_memory.py`) – shared conversation memory stored
  directly in Neo4j as (:Session)-[:HAS_TURN]->(:Turn).
- **Neo4jClient** (`neo4j_client.py`) – small helper around the official Python driver.
- **config.py** – configuration via environment variables and `.env`.

The **Cypher system prompt** in `text_to_cypher_agent.py` is tuned to your
actual Neo4j schema:

- `(:Customer {customerId, name, address, sex, gender, ethnicity})`
- `(:Product {ProductID, Product, ...})`
- `(:Event {EventID, event_type, event_status, ...})`
- Relationships like:
  - `(:Customer)-[:HAS_PRODUCT]->(:Product or :Products)`
  - `(:Customer)-[:HAS_EVENT|HAS_EVENTS]->(:Event or :Events)`

## Getting started

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file at the project root with at least:

   ```env
   OPENAI_API_KEY=your-openai-key
   NEO4J_URI=neo4j+s://your-host:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your-password

   # Optional (for Google ADK / A2A)
   GCP_PROJECT_ID=your-gcp-project
   GCP_LOCATION=us-central1
   COHORT_AGENT_ID=find-cohort-agent
   SUMMARIZATION_AGENT_ID=summarization-agent
   ```

4. Ensure your Neo4j database is populated using the CSVs you provided
   (`neo_customers.csv`, `neo_products.csv`, `neo_events.csv`,
   `neo_cust_product_relationships.csv`, `neo_customer_event_relationships.csv`)
   with labels and relationships as described.

5. Run the Streamlit app:

   ```bash
   streamlit run app_streamlit.py
   ```

6. Ask questions such as:

   - `What are the products customer with id CUST0007 has with us?`
   - `Are there any open events from this customer with name John Doe?`

The orchestrator will:

- Call the **TextToCypher agent** to ask Neo4j.
- Call the **Find Cohorts** ADK agent (currently stubbed).
- Call the **Summarization** ADK agent (currently stubbed).
- Store the conversation history in Neo4j as shared memory.
