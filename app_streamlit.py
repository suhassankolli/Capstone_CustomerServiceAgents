import streamlit as st
import uuid

from orchestrator_agent import OrchestratorAgent

st.set_page_config(page_title="Customer Service Agentic App", page_icon="🤖")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

orchestrator = OrchestratorAgent()

st.title("Customer Service Agentic Application")

st.markdown(
    "Ask natural-language questions like **'What are the products customer with "
    "id CUST0007 has with us?'** or **'Are there any open events from this "
    "customer with name John Doe?'**."
)

customer_id = st.text_input(
    "Customer ID (optional)",
    value="",
    help="If provided, memory and cohort lookups can be linked to this customer.",
)

# display existing chat
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

user_input = st.chat_input("Ask a question about the customer...")

if user_input:
    # show user message
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = orchestrator.handle_query(
                session_id=st.session_state.session_id,
                query=user_input,
                customer_id=customer_id or None,
            )
            answer = result["answer"]
            st.markdown(answer)

            with st.expander("Debug: generated Cypher and raw outputs"):
                st.markdown("**Generated Cypher**")
                st.code(result["text_to_cypher"].get("cypher", ""), language="cypher")

                st.markdown("**Cypher rows (JSON)**")
                st.json(result["text_to_cypher"].get("rows", []))

                st.markdown("**Cohort agent result**")
                st.json(result["cohort"])

    st.session_state.chat_history.append(("assistant", answer))
