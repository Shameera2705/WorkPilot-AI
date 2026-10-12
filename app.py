"""Optional Streamlit UI for running WorkPilot."""
import os
import streamlit as st
from dotenv import load_dotenv
from agent import WorkPilotAgent
from demo import run_offline_demo
from storage import recent_runs
from tools import REPORT_FILE

load_dotenv()
st.set_page_config(page_title="WorkPilot AI", page_icon="🧭", layout="wide")
st.title("🧭 WorkPilot AI")
st.caption("Autonomous enterprise task execution — tool use, audit logs, and independent verification")

with st.sidebar:
    st.subheader("Runtime")
    st.write("LLM API:", "Configured" if os.getenv("OPENAI_API_KEY") else "Not configured")
    st.write("Mode: LLM agent" if os.getenv("OPENAI_API_KEY") else "Mode: offline demo available")

task = st.text_area("Task goal", value="Triage the support tickets, consult relevant internal guidance, create a prioritized action plan, save it, and verify all urgent ticket IDs are covered.", height=110)
c1, c2 = st.columns(2)
with c1:
    if st.button("Run LLM agent", type="primary", disabled=not bool(os.getenv("OPENAI_API_KEY"))):
        with st.spinner("Agent is planning and executing tools..."):
            result = WorkPilotAgent().run(task)
        st.session_state["last_result"] = result
with c2:
    if st.button("Run offline demo"):
        with st.spinner("Running deterministic demo..."):
            result = run_offline_demo()
        st.session_state["last_result"] = result

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    st.subheader("Run result")
    st.json(result)
    st.metric("Verification", "PASSED" if result.get("verification", {}).get("passed") else "NOT VERIFIED")
    if REPORT_FILE.exists():
        st.subheader("Generated report")
        st.markdown(REPORT_FILE.read_text(encoding="utf-8"))

st.subheader("Recent runs")
st.dataframe(recent_runs(), use_container_width=True)
