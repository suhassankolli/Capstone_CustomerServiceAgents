from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from config import OPENAI_API_KEY, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY or ""

# Explicit domain schema based on your uploaded CSVs and Neo4j constraints.
# The LangChain Neo4jGraph will also inject the runtime schema into {schema}.
CYPHER_SYSTEM_PROMPT = """

Task:
You are an expert Neo4j Cypher generator for a retail banking customer graph.

Generate a single READ-ONLY Cypher query that answers the question.

*** Neo4j graph schema ***
{schema}

*** Domain semantics ***
- Customers are stored as nodes with label :Customer.
  - Key identifier: customerId (e.g., "cust_004").
  - Other fields: name, address, sex, gender, ethnicity.
- Products are stored as nodes with label :Product.
  - Key identifier: ProductID.
  - Product types: credit cards, loans, business accounts, etc.
  - Important properties include (if present in schema):
    - Product (product name/description)
    - `Card number`, `Current Balance`, `current balance`, `Credit Limit`, `Card type`
    - `Last Payment Made`, `Has account number`, `open date`, `Maturity date`
    - `Interest rate`, `Maturity amount`, `Bank Name`, `branch name`
    - Business account fields like `Business Name`, `Business Category Type`,
      `Business Account Number`, `number of employees`, `business address`,
      `year of business registration`, `financial_year`, `income`, `expense`, `profit`
    - Loan fields like `Loan number`, `Loan Amount`, `Loan Term (years)`,
      `Loan Interest`, `Current outstanding Loan amount`,
      `Last payment amount`, `Last payment date`.
- Events are stored as nodes with label :Event.
  - Important properties: EventID, event_type, event_message, event_status,
    event_open_date, event_closed_date, customer_notes, customer_service_notes.
- Relationships:
  - (:Customer)-[:HAS_PRODUCT]->(:Product) with {{customerId, productId}}
  - (:Customer)-[:HAS_EVENT]->(:Event) with {{customerId, eventId}}

*** Cypher rules ***
- Use ONLY labels, relationship types, and properties from the schema above.
- The query MUST be read-only:
  - DO NOT use CREATE, MERGE, DELETE, SET, REMOVE, CALL dbms, or any write operations.
- When the question mentions:
  - "customer id X" or "customer X" where X looks like an ID (cust_001),
    match by customerId:
      MATCH (c:Customer {{customerId: "cust_001"}})
  - A name like "John Doe", match by partial string:
      MATCH (c:Customer)
      WHERE c.name CONTAINS "John Doe"
- When accessing properties with spaces, ALWAYS backtick them, e.g.:
    p.`Card number`, p.`Current Balance`, p.`Loan Term (years)`
- For balances, amounts, limits, income, etc., use >, <, >=, <= numeric comparisons.
- For events with "open", "closed", use event_status and/or event_open_date/event_closed_date.
- Always RETURN only the fields that are required to answer the question,
  with clear aliases (AS) when helpful.

*** Few-shot examples ***

Example 1:
Question:
"get me products customer cust_004 has"

Cypher:
MATCH (c:Customer {{customerId: "cust_004"}})-[:HAS_PRODUCT]->(p:Product)
RETURN
  c.customerId AS customerId,
  p.ProductID AS productId,
  p.Product AS productName

Example 2:
Question:
"List credit card products for customer cust_010 with current balance over 1000"

Cypher:
MATCH (c:Customer {{customerId: "cust_010"}})-[:HAS_PRODUCT]->(p:Product)
WHERE p.`Card type` = "Credit Card"
  AND p.`Current Balance` > 1000
RETURN
  c.customerId AS customerId,
  p.ProductID AS productId,
  p.Product AS productName,
  p.`Current Balance` AS currentBalance

Example 3:
Question:
"Show all open events for customer cust_020 and include event type and message"

Cypher:
MATCH (c:Customer {{customerId: "cust_020"}})-[:HAS_EVENT]->(e:Event)
WHERE e.event_status = "open"
RETURN
  c.customerId AS customerId,
  e.EventID AS eventId,
  e.event_type AS eventType,
  e.event_message AS eventMessage,
  e.event_open_date AS eventOpenDate

*** Your task ***

Now generate ONLY the Cypher query for the user question below.
Do NOT include explanations or comments.
Do NOT include backticks around labels or relationship types.
Do backtick property names that contain spaces.

User question:
{question}
"""



class TextToCypherAgent:
    """NL -> Cypher -> execute on Neo4j and return JSON-like result."""

    def __init__(self):
        self.graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USER,
            password=NEO4J_PASSWORD,
        )

        self.graph.refresh_schema()

        #print(self.graph.schema)

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        cypher_prompt = PromptTemplate(
            template=CYPHER_SYSTEM_PROMPT,
            input_variables=["schema", "question"],
        )

        print("---------------- cypher prompt ---------------\n")
       # print(cypher_prompt)
        print("---------------- end cypher prompt ---------- \n")
        self.chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            cypher_prompt=cypher_prompt,
            verbose=True,
            allow_dangerous_requests=True ,
            return_intermediate_steps=True,
        )

    def query(self, nl_query: str) -> dict:
        """Return answer, generated Cypher, and raw rows."""
        print(f" Query --{nl_query}")
        result = self.chain.invoke({"query": nl_query})
        #print("-------- After result call ---------")
        #print(result)
        #print("------------ End ----------")
        cypher = result["intermediate_steps"][0]["query"]
        rows = result["intermediate_steps"][1]["context"]
        answer = result["result"]
        return {
            "answer": answer,
            "cypher": cypher,
            "rows": rows,
        }
