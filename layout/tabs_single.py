import streamlit as st
from utils.column_selector import get_important_columns
from utils.visualizer import visualize_from_llm_response
from utils.insight_suggester import generate_insights, generate_insight_suggestions
from utils.llm_selector import get_llm
from utils.chat_handler import handle_user_query_dynamic
from utils.error_handler import safe_llm_call
import pandas as pd
import re
import json
from utils.pdf_exporter import generate_pdf_report, export_to_pptx

def render_single_tabs():
    if st.session_state["current_session"] is None:
        st.info("Please upload a dataset to continue.")
        return

    session = st.session_state["dataset_sessions"][st.session_state["current_session"]]
    df = session["df"]

    tab1, tab2, tab3 = st.tabs(["📋 Data Preview", "🧠 Insights", "📈 Visualizations"])

    # ==================== Tab 1: Data Preview ==================== #
    with tab1:
        st.header("📋 Dataset Summary & Column Selection")

        st.write(f"Total Rows: {df.shape[0]}")
        st.write(f"Total Columns: {df.shape[1]}")

        st.subheader("👁 Dataset Preview")
        sample_rows = st.slider("Preview Rows Limit", 0, 100, 10, key="sample_rows_single")
        st.dataframe(df.head(sample_rows), use_container_width=True)

        st.subheader("🗂 Column Selection")
        important_cols = get_important_columns(df.to_csv(index=False))
        user_selected_cols = st.multiselect("Select Additional Columns", df.columns.tolist(), default=important_cols)

        final_cols = list(set(important_cols + user_selected_cols))
        session["column_selection"] = final_cols

        st.write(f"Selected Columns: {final_cols}")
        st.dataframe(df[final_cols].head(), use_container_width=True)

    # ==================== Tab 2: Insights ==================== #
    with tab2:
        st.header("🧠 Insights")

        col_left, col_right = st.columns([7, 3], gap="large")

        with col_left:
            st.markdown("### 📋 Generated Insights")
            if session["selected_insight_results"]:
                for insight in session["selected_insight_results"][::-1]:
                    with st.container(border=True):
                        st.markdown(f"**🔍 {insight['question']}**")
                        st.markdown(insight["result"])
                        st.markdown("---")
            else:
                st.info("Please select an insight question from the right to view the results.")

        with col_right:
            st.markdown("### 🔍 Insight Categories")

            if not session["insight_categories"]:
                try:
                    preview = df.head(10).to_csv(index=False)[:2048]
                    llm = get_llm("groq")

                    prompt = f"""
                    I have the following dataset preview:
                    {preview}

                    Please generate 5-6 analytical insight categories with 4-6 detailed questions each.
                    Return strictly in JSON format:
                    [
                        {{"title": "Category Name", "questions": ["Question 1", "Question 2", "Question 3"]}},
                        ...
                    ]
                    """

                    response = llm(prompt)
                    if hasattr(response, "content"):
                        response = response.content

                    json_string = re.search(r"\[.*\]", response, re.DOTALL).group(0)
                    categories = json.loads(json_string)
                    session["insight_categories"] = categories
                    st.toast("✅ Categories loaded successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Insight suggestion failed: {e}")
                    session["insight_categories"] = []

            for idx, category in enumerate(session["insight_categories"]):
                with st.expander(f"📂 {category['title']}", expanded=False):
                    for question in category["questions"]:
                        if st.button(f"🔎 {question}", key=f"insight_{idx}_{question}"):
                            try:
                                result = generate_insights(df, question, "groq")
                                session["selected_insight_results"].append({"question": question, "result": result})
                                st.rerun()
                            except Exception as e:
                                st.error(f"Insight generation failed: {e}")

    # ==================== Tab 3: Visualizations ==================== #
    with tab3:
        st.header("📈 Visualizations")

        if not session.get("column_selection"):
            st.warning("Please select columns in Tab 1 to visualize.")
            st.stop()

        x_axis = st.selectbox("Select X-Axis", session["column_selection"], key="single_visual_x")
        y_axis = st.selectbox("Select Y-Axis", session["column_selection"], key="single_visual_y")
        chart_type = st.selectbox("Chart Type", ["bar", "line", "scatter", "box", "violin", "area", "pie"], key="single_visual_chart")

        if x_axis and y_axis:
            try:
                llm_response = {"chart_type": chart_type, "x": x_axis, "y": y_axis, "group_by": None}
                fig, explanation = visualize_from_llm_response(df, f"{x_axis} vs {y_axis}", llm_response)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    session["visualization_history"].append(f"{chart_type} chart: {x_axis} vs {y_axis}")
                    st.caption(explanation)
            except Exception as e:
                st.error(f"Visualization failed: {e}")

    # ==================== Chatbot (Common for all tabs) ==================== #
    st.markdown("---")
    st.subheader("💬 Chat With Your Dataset")

    user_prompt = st.chat_input("Ask a question about your dataset...", key="single_chat_input")
    if user_prompt:
        with st.spinner("Thinking..."):
            result = safe_llm_call(handle_user_query_dynamic, user_prompt, df, "groq", default={"response": "No response."})
        session["chat_history"].append({"user": user_prompt, "assistant": result})

    for msg in session["chat_history"][::-1]:
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant"):
            st.markdown(msg["assistant"].get("response", msg["assistant"]))
    from utils.pdf_exporter import generate_pdf_report, export_to_pptx

    st.markdown("---")
    st.subheader("📁 Export Report")

    col1, col2 = st.columns(2)
    with col1:
     if st.button("📄 Export PDF (Single Dataset)", key="export_single_pdf"):
        try:
            pdf_path = generate_pdf_report(session)
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", f, file_name="single_dataset_report.pdf")
        except Exception as e:
            st.error(f"Failed to export PDF: {e}")

    with col2:
     if st.button("📊 Export PPTX (Single Dataset)", key="export_single_pptx"):
        try:
            pptx_path = export_to_pptx(session)
            with open(pptx_path, "rb") as f:
                st.download_button("Download PPTX", f, file_name="single_dataset_report.pptx")
        except Exception as e:
            st.error(f"Failed to export PPTX: {e}")
