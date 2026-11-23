import streamlit as st
from database import init_db, save_test_cases, get_all_history, delete_history_item
from agent import run_test_case_agent
from export_utils import test_cases_to_dataframe, convert_df_to_csv

st.set_page_config(
    page_title="AI Test Case Generator Agent",
    page_icon="🧪",
    layout="wide"
)

# Initialize SQLite database
init_db()

# Custom clean styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🧪 AI Test Case Generator Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Convert plain-language software requirements into structured Positive, Negative, and Edge-Case test scenarios using a local LLM (Ollama + LangChain).</div>',
    unsafe_allow_html=True
)

# Session state setup
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "current_requirement" not in st.session_state:
    st.session_state.current_requirement = ""
if "editable_test_cases" not in st.session_state:
    st.session_state.editable_test_cases = []

# Sidebar: Configuration & Saved History
with st.sidebar:
    st.header("⚙️ Agent Settings")
    model_name = st.text_input("Local Ollama Model", value="llama3.2")
    st.caption("Ensure Ollama is running locally before generating test cases.")

    st.divider()
    st.header("🗂️ Saved Test Case History")
    history_records = get_all_history()

    if not history_records:
        st.info("No saved test cases yet. Generate and save a run to view it here.")
    else:
        for rec in history_records:
            label = f"#{rec['id']} | {rec['feature_summary'][:32]}... ({rec['created_at']})"
            with st.expander(label):
                st.write(f"*Requirement:* {rec['requirement']}")
                st.write(f"*Total Test Cases:* {len(rec['test_cases'])}")
                col_load, col_del = st.columns(2)
                with col_load:
                    if st.button("📂 Load", key=f"load_{rec['id']}", use_container_width=True):
                        st.session_state.current_requirement = rec["requirement"]
                        st.session_state.current_result = {
                            "status": "success",
                            "feature_name": rec["feature_summary"],
                            "feature_summary": rec["feature_summary"],
                            "assumptions": [],
                            "scenario_categories": ["Positive", "Negative", "Edge Case"]
                        }
                        st.session_state.editable_test_cases = rec["test_cases"]
                        st.rerun()
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_{rec['id']}", use_container_width=True):
                        delete_history_item(rec["id"])
                        st.rerun()

# Main Area: Requirement Input
st.subheader("1. Enter Software Feature Requirement")

requirement_input = st.text_area(
    "Describe the software feature or user story in plain English:",
    value=st.session_state.current_requirement,
    height=120,
    placeholder="Example: A user should be able to register using name, email, and password. Password must be at least 8 characters."
)

col_cat, col_btn = st.columns([3, 1])
with col_cat:
    selected_scenarios = st.multiselect(
        "Scenario Categories to Include:",
        options=["Positive", "Negative", "Edge Case"],
        default=["Positive", "Negative", "Edge Case"]
    )
with col_btn:
    st.write("")
    st.write("")
    generate_clicked = st.button("🚀 Generate Test Cases", type="primary", use_container_width=True)

if generate_clicked:
    if not requirement_input.strip():
        st.warning("⚠️ Please enter a software requirement before clicking Generate Test Cases.")
    elif not selected_scenarios:
        st.warning("⚠️ Please select at least one scenario category (Positive, Negative, or Edge Case).")
    else:
        with st.spinner("🤖 AI Agent is analyzing the requirement and generating structured test cases..."):
            result = run_test_case_agent(
                requirement=requirement_input,
                selected_categories=selected_scenarios,
                model_name=model_name.strip() or "llama3.2"
            )

        if result["status"] == "error":
            st.error(f"❌ {result['message']}")
        elif result["status"] == "clarification_needed":
            st.warning(f"🤔 Clarification Needed: {result['message']}")
        else:
            st.session_state.current_requirement = requirement_input.strip()
            st.session_state.current_result = result
            st.session_state.editable_test_cases = result["test_cases"]
            st.success(f"✅ Generated {len(result['test_cases'])} structured test cases!")

# Results, Review, Edit, Delete, Save & Export Section
if st.session_state.current_result and st.session_state.editable_test_cases:
    res = st.session_state.current_result
    st.divider()
    st.subheader("2. Agent Requirement Analysis")

    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown(f"*Identified Feature:* {res.get('feature_name', 'N/A')}")
        st.markdown(f"*Testing Purpose:* {res.get('feature_summary', 'N/A')}")
    with info_col2:
        assumptions = res.get("assumptions", [])
        if assumptions:
            st.markdown("*Assumptions Noted:*")
            for a in assumptions:
                st.markdown(f"- {a}")
        else:
            st.markdown("*Assumptions Noted:* Based strictly on provided requirement.")

    st.subheader("3. Review, Edit & Manage Test Cases")
    st.caption("💡 Tip: Double-click any cell to edit text/priority. Select a row checkbox on the left and press Delete key to remove a test case.")

    df_current = test_cases_to_dataframe(st.session_state.editable_test_cases)

    edited_df = st.data_editor(
        df_current,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "test_case_id": st.column_config.TextColumn("ID", width="small"),
            "title": st.column_config.TextColumn("Test Case Title", width="medium"),
            "scenario_type": st.column_config.SelectboxColumn(
                "Scenario Type",
                options=["Positive", "Negative", "Edge Case"],
                width="small"
            ),
            "preconditions": st.column_config.TextColumn("Preconditions", width="medium"),
            "test_steps": st.column_config.TextColumn("Test Steps", width="large"),
            "test_data": st.column_config.TextColumn("Test Data", width="medium"),
            "expected_result": st.column_config.TextColumn("Expected Result", width="large"),
            "priority": st.column_config.SelectboxColumn(
                "Priority",
                options=["High", "Medium", "Low"],
                width="small"
            )
        },
        key="test_case_editor"
    )

    updated_records = edited_df.to_dict(orient="records")
    st.session_state.editable_test_cases = updated_records

    st.warning("⚠️ Note: AI-generated test cases should be reviewed by a QA tester before actual test execution.")

    # Action Buttons: Save to SQLite & Export CSV
    btn_col1, btn_col2, _ = st.columns([1.2, 1.2, 2])
    with btn_col1:
        if st.button("💾 Save Test Cases to Database", use_container_width=True):
            if not updated_records:
                st.error("Cannot save an empty test case list.")
            else:
                save_test_cases(
                    requirement=st.session_state.current_requirement,
                    feature_summary=res.get("feature_summary", "Software Feature"),
                    test_cases=updated_records
                )
                st.success("✅ Test cases saved to SQLite database! Check the sidebar history.")
                st.rerun()

    with btn_col2:
        csv_bytes = convert_df_to_csv(updated_records)
        st.download_button(
            label="📥 Download CSV",
            data=csv_bytes,
            file_name="generated_test_cases.csv",
            mime="text/csv",
            use_container_width=True
        )