from __future__ import annotations

import asyncio
from typing import List, Dict, Any, Optional

from google.genai.types import UserContent, Part
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner


SUMMARY_SYSTEM_PROMPT = """
You are a summarization agent for a banking customer support / analytics system.

You will receive:
- The user's original natural language query
- A Text-to-Cypher / graph query result
- A cohort lookup result
- Recent conversation context

You MUST ALWAYS respond in the EXACT following textual format,
even if some sections have no information (in that case, say "None"):

Graph insight: <short, concise explanation based on the text_to_cypher_result>
Customer cohorts: <comma-separated list of cohorts or 'None'>
Special open events: <semicolon-separated list of important open events or 'None'>
Final Response: Final summary using all the data in small paragraph
Rules:
- Do NOT add any extra headings or sections.
- Do NOT include JSON or bullet points.
- Keep the answer short and business-friendly.
- Do NOT Show duplicate records or answers
""".strip()


class SummarizationAgent:
    """
    LLM-based summarization agent using LlmAgent and InMemoryRunner.

    This agent:
      - Builds a structured user message from orchestrator outputs
      - Delegates summarization to an LLM with a strong system prompt
      - Maintains an in-memory session for conversational continuity
    """

    def __init__(
        self,
        app_name: str = "SummarizerApp",
        model: str = "gemini-2.5-flash-lite",
        user_id: str = "summarization_user",
        debug: bool = False,
    ) -> None:
        self._user_id = user_id
        self._debug = debug

        # LLM agent responsible for text generation
        self._llm_agent = LlmAgent(
            name="CustSvcSummarizeAgent",
            model=model,
            instruction=SUMMARY_SYSTEM_PROMPT,
            output_key="summary",
        )

        # Runner for executing the agent
        self._runner = InMemoryRunner(
            agent=self._llm_agent,
            app_name=app_name,
        )

        # Lazy-created and reused session
        self._session: Optional[Any] = None

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #

    def _log(self, *args: Any) -> None:
        """Simple debug logger."""
        if self._debug:
            print(*args)

    def _build_user_message(self, payload: Dict[str, Any]) -> str:
        """Flatten the structured payload into a single user message string."""

        original_query = payload.get("original_query", "")
        t2c = payload.get("text_to_cypher_result", {})
        cohort = payload.get("cohort_result", {})
        conversation_context: List[Dict[str, Any]] = payload.get(
            "conversation_context", []
        )

        # Make the context human-readable for the LLM
        context_lines: List[str] = []
        for turn in conversation_context:
            role = turn.get("role", "user")
            text = turn.get("text", "")
            customer_id = turn.get("customer_id")
            if customer_id:
                context_lines.append(f"[{role}] ({customer_id}): {text}")
            else:
                context_lines.append(f"[{role}]: {text}")

        context_str = "\n".join(context_lines) if context_lines else "No prior context."

        user_message = f"""
        Original user query:
        {original_query}

        Text-to-Cypher / graph result (raw):
        {t2c}

        Cohort result (raw):
        {cohort}

        Recent conversation context:
        {context_str}

        Using ALL of the information above, produce the final answer in the required format.
        Remember:
        Graph insight: ...
        Customer cohorts: ...
        Special open events: ...
        Final summary using all the data in small paragraph
        Rules:
        - Do NOT add any extra headings or sections.
        - Do NOT include JSON or bullet points.
        - Keep the answer short and business-friendly.
        - Do NOT Show duplicate records or answers
        """.strip()

        return user_message

    async def _create_session_async(self) -> Any:
        """Create an ADK session for this user."""
        return await self._runner.session_service.create_session(
            app_name=self._runner.app_name,
            user_id=self._user_id,
        )

    def _get_or_create_session(self) -> Any:
        """Get the existing session or create a new one."""
        if self._session is None:
            self._session = asyncio.run(self._create_session_async())
            self._log(f"Created new session: {self._session.id}")
        return self._session

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #

    def summarize(
        self,
        original_query: str,
        text_to_cypher_result: Dict[str, Any],
        cohort_result: Dict[str, Any],
        conversation_context: List[Dict[str, Any]],
    ) -> str:
        """
        Summarize the combined agent outputs via LlmAgent.

        Args:
            original_query: User's original NL query.
            text_to_cypher_result: Result of the graph/Text-to-Cypher agent.
            cohort_result: Result of the cohort agent.
            conversation_context: Recent conversation history.

        Returns:
            A formatted summary string following SUMMARY_SYSTEM_PROMPT rules.
        """

        payload = {
            "original_query": original_query,
            "text_to_cypher_result": text_to_cypher_result,
            "cohort_result": cohort_result,
            "conversation_context": conversation_context,
        }

        #self._log("-------- Original Query ---------")
        #self._log(original_query)

        user_message_str = self._build_user_message(payload)

        #self._log("--- Start User Message ----")
        #self._log(user_message_str)
        #self._log("--- End User Message ----")

        user_message = UserContent(parts=[Part(text=user_message_str)])
        session = self._get_or_create_session()

        summary_chunks: List[str] = []

        for event in self._runner.run(
            user_id=self._user_id,
            session_id=session.id,
            new_message=user_message,
        ):
            # Events can be tool calls, internal state, etc. We only care about text parts.
            content = getattr(event, "content", None)
            if not content:
                continue

            for part in getattr(content, "parts", []) or []:
                text = getattr(part, "text", None)
                if text:
                    summary_chunks.append(text)

        response = "".join(summary_chunks).strip()

        self._log("--- Start Response ----")
        self._log(response)
        self._log("--- End Response ----")

        return response
