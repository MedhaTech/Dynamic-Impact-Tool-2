import os
import json
import re
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
from utils.file_loader import load_data, clean_data
from utils.chat_handler import handle_user_query_dynamic
from utils.visualizer import visualize_from_llm_response
from utils.pdf_exporter import generate_pdf_report, export_to_pptx
from utils.error_handler import safe_llm_call
from utils.insight_suggester import generate_insight_suggestions, generate_insights
from utils.column_selector import get_important_columns
from utils.llm_selector import get_llm

load_dotenv()
st.set_page_config(page_title="Dynamic Impact Tool", layout="wide")

# ✅ Session Initialization
if "dataset_sessions" not in st.session_state:
    st.session_state["dataset_sessions"] = {}

if "current_session" not in st.session_state:
    st.session_state["current_session"] = None

# ========================= Sidebar =========================
with st.sidebar:
    st.title("Dynamic Impact Tool")
    model_source = st.selectbox("Model", ["groq", "ollama"], key="sidebar_model")
    # Dataset Upload
    st.subheader("📁 Upload Dataset")
    uploaded_file = st.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"])
    file_path = st.text_input("Or Enter File Path")

    # Dataset History
    st.subheader("🕒 Dataset History")
    dataset_names = list(st.session_state["dataset_sessions"].keys())
    if dataset_names:
        selected_history = st.radio("Select Dataset", dataset_names, index=dataset_names.index(st.session_state["current_session"]) if st.session_state["current_session"] else 0)
        st.session_state["current_session"] = selected_history

    st.subheader("🔗 Navigation")
    tab = st.radio("Choose View", ["Upload & Visualize", "Insights", "Summary & Export"])

# ========================= Upload Logic =========================
if uploaded_file is not None:
    file_name = uploaded_file.name
    file_bytes = uploaded_file.read()
    file_like = BytesIO(file_bytes)
    df, _ = load_data(file_like, file_name)
    df = clean_data(df)

    if file_name not in st.session_state["dataset_sessions"]:
        st.session_state["dataset_sessions"][file_name] = {
            "df": df,
            "chat_history": [],
            "insight_categories": [],
            "selected_insight_results": [],
            "visualization_history": []
        }

    st.session_state["current_session"] = file_name
    st.toast(f"✅ {file_name} loaded successfully.")
    st.rerun()

if file_path:
    file_name = os.path.basename(file_path)
    try:
        file = open(file_path, "rb")
        df, _ = load_data(file, file_name)
        df = clean_data(df)

        if file_name not in st.session_state["dataset_sessions"]:
            st.session_state["dataset_sessions"][file_name] = {
                "df": df,
                "chat_history": [],
                "insight_categories": [],
                "selected_insight_results": [],
                "visualization_history": []
            }

        st.session_state["current_session"] = file_name
        st.toast(f"✅ {file_name} loaded successfully.")
        st.rerun()

    except Exception as e:
        st.error(f"File not found: {e}")

# ========================= Upload & Visualize =========================
if tab == "Upload & Visualize":
    current_session = st.session_state["current_session"]

    if current_session:
        dataset = st.session_state["dataset_sessions"][current_session]
        df = dataset["df"]

        st.header(f"📄 Dataset: {current_session}")

        # Dataset Preview
        sample_rows = st.slider("Preview Rows Limit (for display only)", 0, 100, 10, key=f"sample_slider_{current_session}")
        with st.expander("🔍 Dataset Preview"):
            if sample_rows > 0:
                st.dataframe(df.head(sample_rows), use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)

        # Column Selection
        st.subheader("🧠 Column Selection")
        important_cols = get_important_columns(df.to_csv(index=False))

        if important_cols:
            st.success(f"AI selected {len(important_cols)} important columns.")
            with st.expander("🔍 Preview AI-Selected Columns"):
                st.dataframe(df[important_cols].head(), use_container_width=True)
        else:
            st.warning("⚠️ AI failed to suggest important columns.")
            important_cols = []

        user_selected_cols = st.multiselect("✅ Select Additional Columns", options=df.columns.tolist(), default=important_cols, key=f"user_cols_{current_session}")
        final_cols = list(set(important_cols + user_selected_cols))

        if final_cols:
            st.success(f"Total columns selected: {len(final_cols)}")
            st.dataframe(df[final_cols].head(), use_container_width=True)

        # Visualization
        st.subheader("📈 Visualization")
        x_axis = st.selectbox("Select X-Axis", final_cols, key=f"x_axis_{current_session}")
        y_axis = st.selectbox("Select Y-Axis", final_cols, key=f"y_axis_{current_session}")
        chart_type = st.selectbox("Chart Type", ["bar", "line", "scatter", "box", "violin", "area", "pie"], key=f"chart_type_{current_session}")

        if x_axis and y_axis:
            try:
                llm_response = {"chart_type": chart_type, "x": x_axis, "y": y_axis, "group_by": None}
                fig, explanation = visualize_from_llm_response(df, f"{x_axis} vs {y_axis}", llm_response)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption(explanation)
                    dataset["visualization_history"].append({"x": x_axis, "y": y_axis, "chart": chart_type, "explanation": explanation})
                else:
                    st.warning("No chart could be generated.")
            except Exception as e:
                st.error(f"Visualization failed: {e}")

        # Chat Bot
        st.subheader("💬 Chat With Dataset")
        chat_history = dataset.get("chat_history", [])
        user_prompt = st.chat_input("Ask a question...", key=f"chat_input_{current_session}")
        if user_prompt:
            with st.spinner("Thinking..."):
                result = safe_llm_call(handle_user_query_dynamic, user_prompt, df, model_source, default={"response": "No response."})
            chat_history.append({"user": user_prompt, "assistant": result})
            dataset["chat_history"] = chat_history
            st.rerun()

        for msg in chat_history[::-1]:
            with st.chat_message("user"):
                st.markdown(msg["user"])
            with st.chat_message("assistant"):
                st.markdown(msg["assistant"].get("response", msg["assistant"]))

    else:
        st.info("Please upload or select a dataset from the sidebar.")

# ========================= Insights Tab =========================
if tab == "Insights":
    current_session = st.session_state["current_session"]

    if current_session:
        dataset = st.session_state["dataset_sessions"][current_session]
        df = dataset["df"]

        st.header(f"🧠 Insights for {current_session}")

        col1, col2 = st.columns([7, 3], gap="large")

        with col1:
            st.subheader("📋 Generated Insights")
            for insight in dataset.get("selected_insight_results", [])[::-1]:
                with st.container(border=True):
                    st.markdown(f"**🔍 {insight['question']}**")
                    st.markdown(insight["result"])
                    st.markdown("---")

        with col2:
            st.subheader("🔍 Insight Categories")

            if not dataset.get("insight_categories"):
                try:
                    preview = df.head(10).to_csv(index=False)[:2048]
                    llm = get_llm("groq")

                    prompt = f"""
                    I have the following dataset preview:
                    {preview}

                    Please generate exactly 5 to 6 analytical insight categories based on this dataset.
                    For each category, provide exactly 4 to 6 detailed analytical questions.

                    ⚠️ IMPORTANT:
                    Return the response strictly in this JSON format:
                    [
                        {{
                            "title": "Category Name",
                            "questions": ["Question 1", "Question 2", "Question 3"]
                        }},
                        ...
                    ]

                    ❗ Do not include any introduction, explanation, or extra text. Only return the JSON array.
                    """

                    response = llm(prompt)
                    if hasattr(response, "content"):
                        response = response.content

                    json_string = re.search(r"\[.*\]", response, re.DOTALL).group(0)
                    categories = json.loads(json_string)
                    dataset["insight_categories"] = categories
                    st.toast("✅ Categories loaded successfully.")
                    st.rerun()

                except Exception as e:
                    st.error(f"Insight suggestion failed: {e}")
                    dataset["insight_categories"] = []

            categories = dataset.get("insight_categories", [])
            for idx, category in enumerate(categories):
                with st.expander(f"📂 {category['title']}", expanded=False):
                    for question in category.get("questions", []):
                        if st.button(f"🔎 {question}", key=f"insight_{current_session}_{idx}_{question}"):
                            with st.spinner("Generating insight..."):
                                try:
                                    result = generate_insights(df, question, model_source)
                                    dataset["selected_insight_results"].append({"question": question, "result": result})
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Insight generation failed: {e}")

        # Chat in Insights
        chat_history = dataset.get("chat_history", [])
        user_prompt = st.chat_input("Ask a question...", key=f"chat_input_insights_{current_session}")
        if user_prompt:
            with st.spinner("Thinking..."):
                result = safe_llm_call(handle_user_query_dynamic, user_prompt, df, model_source, default={"response": "No response."})
            chat_history.append({"user": user_prompt, "assistant": result})
            dataset["chat_history"] = chat_history
            st.rerun()

        for msg in chat_history[::-1]:
            with st.chat_message("user"):
                st.markdown(msg["user"])
            with st.chat_message("assistant"):
                st.markdown(msg["assistant"].get("response", msg["assistant"]))

    else:
        st.info("Please upload or select a dataset from the sidebar.")

# ========================= Summary & Export =========================
if tab == "Summary & Export":
    current_session = st.session_state["current_session"]

    if current_session:
        dataset = st.session_state["dataset_sessions"][current_session]

        st.header(f"📦 Export Summary for {current_session}")

        insights_summary = "\n\n".join([insight["result"] for insight in dataset.get("selected_insight_results", [])])
        chat_logs = dataset.get("chat_history", [])

        st.subheader("Summary & Chat History")
        if insights_summary:
            st.markdown(insights_summary)
        else:
            st.info("No insights to display.")

        for msg in chat_logs[::-1]:
            with st.chat_message("user"):
                st.markdown(msg["user"])
            with st.chat_message("assistant"):
                st.markdown(msg["assistant"].get("response", msg["assistant"]))

        st.subheader("📁 Export Report")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Export PDF"):
                try:
                    pdf_path = generate_pdf_report(insights_summary, chat_logs)
                    with open(pdf_path, "rb") as f:
                        st.download_button("Download PDF", f, file_name=f"{current_session}_summary.pdf")
                except Exception as e:
                    st.error(f"Failed to export PDF: {e}")

        with col2:
            if st.button("📊 Export PPTX"):
                try:
                    pptx_path = export_to_pptx(insights_summary, chat_logs)
                    with open(pptx_path, "rb") as f:
                        st.download_button("Download PPTX", f, file_name=f"{current_session}_summary.pptx")
                except Exception as e:
                    st.error(f"Failed to export PPTX: {e}")

    else:
        st.info("Please upload or select a dataset from the sidebar.")
