from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


class Neo4jClient:
    """Simple wrapper for Neo4j driver."""

    def __init__(self):
        self._driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
        )

    def close(self):
        self._driver.close()

    def run_query(self, cypher: str, params: dict | None = None):
        """Execute Cypher and return list of dictionaries."""
        with self._driver.session() as session:
            result = session.run(cypher, params or {})
            return [record.data() for record in result]
