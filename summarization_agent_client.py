from config import SUMMARIZATION_AGENT_ID, GCP_PROJECT_ID, GCP_LOCATION


class SummarizationAgentClient:
    """Client wrapper for Google ADK summarization agent, via A2A.

    Replace `_call_adk_agent` with your real A2A implementation.
    """

    def __init__(self):
        self.agent_id = SUMMARIZATION_AGENT_ID
        self.project_id = GCP_PROJECT_ID
        self.location = GCP_LOCATION

    def _call_adk_agent(self, payload: dict) -> str:
        # TODO: call your ADK summarization agent here.
        # For now, we build a simple stitched response as a placeholder.
        pieces: list[str] = []

        t2c = payload.get("text_to_cypher_result") or {}
        cohort = payload.get("cohort_result") or {}

        if t2c.get("answer"):
            pieces.append(f"Graph insight: {t2c['answer']}")

        if cohort:
            if cohort.get("cohorts"):
                pieces.append(
                    "Customer cohorts: " + ", ".join(cohort["cohorts"])
                )
            open_events = [
                e for e in cohort.get("events", []) if e.get("status") == "OPEN"
            ]
            if open_events:
                ev_descriptions = [
                    f"{e.get('event_type', 'event')} ({e.get('status', '')})"
                    for e in open_events
                ]
                pieces.append("Special open events: " + "; ".join(ev_descriptions))

        if not pieces:
            pieces.append("No additional information found for this customer.")

        return " ".join(pieces)

    def summarize(
        self,
        original_query: str,
        text_to_cypher_result: dict,
        cohort_result: dict,
        conversation_context: list[dict],
    ) -> str:
        payload = {
            "original_query": original_query,
            "text_to_cpher_result": text_to_cypher_result,
            "cohort_result": cohort_result,
            "conversation_context": conversation_context,
        }
        return self._call_adk_agent(payload)
