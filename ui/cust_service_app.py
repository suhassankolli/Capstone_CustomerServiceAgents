import streamlit as st
import uuid
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from agents.orchestrator_agent import OrchestratorAgent

st.set_page_config(page_title="Customer Service Agentic App", page_icon="🤖")

# -------------------------------------------------------------------
# Session setup
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# Load customers and set up dropdown
# -------------------------------------------------------------------
@st.cache_data
def load_customers(path: str | None = None):
    if path is None:
        path = Path(__file__).parent / "customers.json"
    else:
        path = Path(path)
    with open(path, "r") as f:
        return json.load(f)

customers = load_customers()

# Build options list with a "no customer" option
customer_options = [None] + customers

selected_customer = st.selectbox(
    "Customer (Required)",
    options=customer_options,
    format_func=lambda c: (
        "No customer selected"
        if c is None
        else f"{c['customer_id']} -- {c['name']}"
    ),
    help="Select a customer to link memory and cohort lookups. You can also leave this empty.",
)

# This is what we pass into the orchestrator
selected_customer_id = (
    selected_customer["customer_id"] if selected_customer is not None else None
)

# -------------------------------------------------------------------
# Display existing chat
# -------------------------------------------------------------------
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# -------------------------------------------------------------------
# Handle new user input
# -------------------------------------------------------------------
#user_input = st.chat_input("Ask a question about the customer...")
if selected_customer_id is None:
    st.warning("⚠️ Please select a customer before asking a question.")
    user_input = st.chat_input(
        "Customer selection required...",
        disabled=True
    )
else:
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
                    customer_id=selected_customer_id,  # <-- pass only customer_id
                )
                answer = result["answer"]
                final_response = answer
                if "Final Response:" in answer:
                    final_response = answer.split("Final Response:", 1)[1].strip()

                st.markdown(final_response)
                #st.markdown(answer)

                with st.expander("Debug: generated Cypher and raw outputs"):
                    st.markdown("**Generated Cypher**")
                    st.code(result["text_to_cypher"].get("cypher", ""), language="cypher")

                    st.markdown("**Cypher rows (JSON)**")
                    st.json(result["text_to_cypher"].get("rows", []))

                    st.markdown("**Cohort agent result**")
                    st.json(result["cohort"])

        st.session_state.chat_history.append(("assistant", answer))
