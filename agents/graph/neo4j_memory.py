from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from .neo4j_client import Neo4jClient


class Neo4jMemoryStore:
    """Stores conversational memory in Neo4j.

    Model:
      (:Session {id})-[:HAS_TURN]->(:Turn {role, text, ts})
      Optionally attach to (:Customer {customerId}) via (:Customer)-[:HAS_SESSION]->(:Session)
    """

    def __init__(self, client: Neo4jClient | None = None):
        self.client = client or Neo4jClient()

    def append_turn(
        self,
        session_id: str,
        role: str,
        text: str,
        customer_id: str | None = None,
    ):
        cypher = """

        MERGE (s:Session {id: $session_id})
        ON CREATE SET s.created_at = datetime()
        CREATE (t:Turn {
            id: randomUUID(),
            role: $role,
            text: $text,
            ts: datetime($ts)
        })
        MERGE (s)-[:HAS_TURN]->(t)
        WITH s, t
        CALL {
            WITH s, t
            WITH s, t WHERE $customer_id IS NOT NULL
            MERGE (c:Customer {customerId: $customer_id})
            MERGE (c)-[:HAS_SESSION]->(s)
        }
        RETURN s.id AS session_id
        """

        self.client.run_query(
            cypher,
            {
                "session_id": session_id,
                "role": role,
                "text": text,
                "ts": datetime.utcnow().isoformat(),
                "customer_id": customer_id,
            },
        )

    def get_recent_context(self, session_id: str, limit: int = 10) -> list[dict]:
        cypher = """

        MATCH (s:Session {id: $session_id})-[:HAS_TURN]->(t:Turn)
        RETURN t.role AS role, t.text AS text, t.ts AS ts
        ORDER BY t.ts DESC
        LIMIT $limit
        """

        return self.client.run_query(
            cypher,
            {"session_id": session_id, "limit": limit},
        )
