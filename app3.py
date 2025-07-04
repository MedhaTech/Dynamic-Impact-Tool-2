import os
import json
import re
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
from utils.file_loader import load_data, clean_data
from utils.chat_handler import handle_user_query_dynamic
from utils.visualizer import (
    visualize_from_llm_response,
    visualize_comparison_overlay,
    visualize_comparison_side_by_side
)
from utils.pdf_exporter import generate_pdf_report, export_to_pptx
from utils.error_handler import safe_llm_call
from utils.insight_suggester import (
    generate_insight_suggestions,
    generate_insights,
    generate_comparison_insights
)
from utils.column_selector import get_important_columns
from utils.llm_selector import get_llm

load_dotenv()
st.set_page_config(page_title="Dynamic Impact Tool", layout="wide")

# ========================= Initialize =========================
for key in ["df", "df1", "df2", "insights", "compare_chat", "file_bytes", "file_name", "file_path_used", "just_uploaded"]:
    if key not in st.session_state:
        st.session_state[key] = None

if "dataset_sessions" not in st.session_state:
    st.session_state["dataset_sessions"] = {}

if "current_session" not in st.session_state:
    st.session_state["current_session"] = None

# ========================= Sidebar =========================
# with st.sidebar:
#     st.title("Dynamic Impact Tool")
    # section = st.radio("Navigate", ["Upload & Visualize", "Insights", "Compare Datasets", "Summary & Export"], key="sidebar_section")
    # model_source = st.selectbox("Model", ["groq", "ollama"], key="sidebar_model")

#     st.markdown("## 🗂️ Dataset History")
#     dataset_names = list(st.session_state["dataset_sessions"].keys())

#     if dataset_names:
#         selected_dataset = st.radio("Select Dataset Session", dataset_names, index=dataset_names.index(st.session_state["current_session"]) if st.session_state["current_session"] else 0)
#         st.session_state["current_session"] = selected_dataset
#     else:
#         st.info("No datasets uploaded yet.")

#     st.markdown("---")
#     if st.button("🧹 Clear All Sessions"):
#         st.session_state["dataset_sessions"] = {}
#         st.session_state["current_session"] = None
#         st.experimental_rerun()


with st.sidebar:
    st.title("Dynamic Impact Tool")
    section = st.radio("Navigate", ["Upload & Visualize", "Insights", "Compare Datasets", "Summary & Export"], key="sidebar_section")
    model_source = st.selectbox("Model", ["groq", "ollama"], key="sidebar_model")
    st.markdown("## 📥 Upload Dataset")
    uploaded_file = st.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"], key="sidebar_upload")

    # 👉 Upload processing only when button is clicked
    if st.button("Upload Dataset"):
        if uploaded_file is not None:
            file_name = uploaded_file.name
            file_bytes = uploaded_file.read()
            file_like = BytesIO(file_bytes)
            df, _ = load_data(file_like, file_name)
            df = clean_data(df)

            # Create a session if it doesn't exist
            if file_name not in st.session_state["dataset_sessions"]:
                st.session_state["dataset_sessions"][file_name] = {
                    "df": df,
                    "chat_history": [],
                    "insight_categories": [],
                    "selected_insight_results": [],
                    "visualization_history": [],
                    "column_selection": [],
                    "model_source": "groq"
                }

            st.session_state["current_session"] = file_name
            st.toast(f"✅ {file_name} uploaded successfully.")
            st.rerun()
        else:
            st.warning("Please upload a file first!")

    # 👉 Dataset History Section
    st.markdown("## 🗂️ Dataset History")
    dataset_names = list(st.session_state["dataset_sessions"].keys())

    if dataset_names:
        selected_dataset = st.radio("Select Dataset Session", dataset_names,
                                    index=dataset_names.index(st.session_state["current_session"]) if st.session_state["current_session"] else 0)

        if selected_dataset != st.session_state["current_session"]:
            st.session_state["current_session"] = selected_dataset
            st.toast(f"✅ Switched to {selected_dataset}")
            st.rerun()

        st.markdown("### 📄 Quick Dataset Preview")
        df_preview = st.session_state["dataset_sessions"][st.session_state["current_session"]]["df"].head(3)
        st.dataframe(df_preview, use_container_width=True)

        # 👉 Rename Dataset Feature
        st.markdown("### ✏️ Rename Current Dataset")
        new_name = st.text_input("Enter New Name", placeholder="New dataset name...")
        if st.button("Rename Dataset"):
            if new_name and new_name not in st.session_state["dataset_sessions"]:
                st.session_state["dataset_sessions"][new_name] = st.session_state["dataset_sessions"].pop(st.session_state["current_session"])
                st.session_state["current_session"] = new_name
                st.toast(f"✅ Dataset renamed to {new_name}")
                st.rerun()
            else:
                st.warning("Please enter a unique dataset name.")

    else:
        st.info("No datasets uploaded yet.")

    st.markdown("---")
    if st.button("🧹 Clear All Sessions"):
        st.session_state["dataset_sessions"] = {}
        st.session_state["current_session"] = None
        st.rerun()


# ========================= Upload & Visualize =========================
if section == "Upload & Visualize":
    st.header("📥 Upload Dataset")

    col1, col2 = st.columns(2)
    uploaded_file = col1.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"], key="upload_main2")
    file_path = col2.text_input("Or Enter File Path", key="path_main")

    if uploaded_file is not None:
        file_name = uploaded_file.name
        st.session_state["file_bytes"] = uploaded_file.read()
        st.session_state["file_name"] = file_name
        st.session_state["file_path_used"] = None

        if file_name not in st.session_state["dataset_sessions"]:
            st.session_state["dataset_sessions"][file_name] = {
                "df": None,
                "chat_history": [],
                "insight_categories": [],
                "selected_insight_results": [],
                "visualization_history": []
            }
        st.session_state["current_session"] = file_name

    if file_path:
        st.session_state["file_path_used"] = file_path.strip()
        st.session_state["file_bytes"] = None
        st.session_state["file_name"] = None

    if st.session_state["df"] is None:
        if st.session_state.get("file_bytes"):
            with st.spinner("Loading uploaded file..."):
                file_like = BytesIO(st.session_state["file_bytes"])
                df, _ = load_data(file_like, st.session_state["file_name"])
                df = clean_data(df)
                st.session_state["df"] = df
                st.session_state["dataset_sessions"][st.session_state["current_session"]]["df"] = df
                st.toast(f"✅ {st.session_state['file_name']} loaded successfully.")
        elif st.session_state.get("file_path_used"):
            try:
                with st.spinner("Loading file from path..."):
                    file = open(st.session_state["file_path_used"], "rb")
                    df, _ = load_data(file, st.session_state["file_name"])
                    df = clean_data(df)
                    st.session_state["df"] = df
                    st.session_state["dataset_sessions"][st.session_state["current_session"]]["df"] = df
                    st.toast(f"✅ {st.session_state['file_path_used']} loaded successfully.")
            except Exception as e:
                st.error(f"❌ File not found: {e}")
    else:
        df = st.session_state["df"]
        st.info(f"✅ Dataset already loaded with {len(df)} rows and {len(df.columns)} columns.")

    if "df" in st.session_state and st.session_state["df"] is not None:
        df = st.session_state["df"]
        session_data = st.session_state["dataset_sessions"][st.session_state["current_session"]]

        sample_rows = st.slider("Preview Rows Limit (for display only)", 0, 100, 10, key="sample_rows_upload")
        with st.expander("🔍 Dataset Preview"):
            st.dataframe(df.head(sample_rows) if sample_rows > 0 else df, use_container_width=True)

        st.markdown("## 🧠 AI-Selected + User-Selected Columns")
        important_cols = get_important_columns(df.to_csv(index=False), model_source=model_source)

        if important_cols:
            st.success(f"AI selected {len(important_cols)} important columns.")
            with st.expander("🔍 Preview AI-Selected Columns"):
                st.dataframe(df[important_cols].head(), use_container_width=True)
        else:
            st.warning("⚠️ AI failed to suggest important columns.")
            important_cols = []

        user_selected_cols = st.multiselect("✅ Select Additional Columns for Your Contextual Analysis", options=df.columns.tolist(), default=important_cols, key="manual_col_select")

        final_cols = list(set(important_cols + user_selected_cols))

        if final_cols:
            st.success(f"Total columns selected for analysis: {len(final_cols)}")
            st.dataframe(df[final_cols].head(), use_container_width=True)

        st.markdown("## 📈 Visualization")
        x_axis = st.selectbox("Select X-Axis", final_cols, key="x_axis")
        y_axis = st.selectbox("Select Y-Axis", final_cols, key="y_axis")
        chart_type = st.selectbox("Chart Type", ["bar", "line", "scatter", "box", "violin", "area", "pie"], key="chart_type")

        if x_axis and y_axis and x_axis in df.columns and y_axis in df.columns:
            try:
                llm_response = {"chart_type": chart_type, "x": x_axis, "y": y_axis, "group_by": None}
                fig, explanation = visualize_from_llm_response(df, f"{x_axis} vs {y_axis}", llm_response)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption(explanation)
                    session_data["visualization_history"].append({
                        "x_axis": x_axis,
                        "y_axis": y_axis,
                        "chart_type": chart_type
                    })
                else:
                    st.warning("No chart could be generated.")
            except Exception as e:
                st.error(f"Visualization failed: {e}")
        else:
            st.info("Please select valid X and Y columns to generate visualization.")

        st.markdown("## 💬 Ask Your Data")
        user_prompt = st.chat_input("💬 Ask a question about your dataset...")

        if user_prompt:
            with st.spinner("Thinking..."):
                result = safe_llm_call(handle_user_query_dynamic, user_prompt, st.session_state["df"], model_source, default={"response": "No response."})
            session_data["chat_history"].append({"user": user_prompt, "assistant": result})

        for msg in session_data["chat_history"][::-1]:
            with st.chat_message("user"):
                st.markdown(msg["user"])
            with st.chat_message("assistant"):
                st.markdown(msg["assistant"].get("response", msg["assistant"]))

# ========================= Insights =========================
if section == "Insights":
    st.markdown("## 🧠 Insight Discovery Center")
    st.markdown("---")

    if st.session_state.get("current_session"):
        session_data = st.session_state["dataset_sessions"][st.session_state["current_session"]]
        df = session_data["df"]

        with st.container():
            col1, col2 = st.columns([7, 3], gap="large")

            with col1:
                st.markdown("### 📋 Generated Insights")
                if session_data.get("selected_insight_results"):
                    for insight in session_data["selected_insight_results"][::-1]:
                        with st.container(border=True):
                            st.markdown(f"**🔍 {insight['question']}**")
                            st.markdown(insight["result"])
                            st.markdown("---")
                else:
                    st.info("Please select an insight question from the right to view the results.")

            with col2:
                st.markdown("## 🔍 Insight Categories")

                if session_data.get("insight_categories"):
                    for idx, category in enumerate(session_data["insight_categories"]):
                        with st.expander(f"📂 {category['title']}"):
                            for question in category.get("questions", []):
                                if st.button(f"🔎 {question}", key=f"insight_{idx}_{question}"):
                                    with st.spinner("Generating insight..."):
                                        try:
                                            result = generate_insights(df, question, model_source)
                                            session_data["selected_insight_results"].append({"question": question, "result": result})
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Insight generation failed: {e}")
                else:
                    try:
                        preview = df.head(10).to_csv(index=False)[:2048]
                        llm = get_llm(model_source)

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

                        session_data["insight_categories"] = categories
                        st.toast("✅ Categories loaded successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Insight suggestion failed: {e}")
                        session_data["insight_categories"] = []

        st.markdown("---")
        user_prompt = st.chat_input("💬 Ask a question about your dataset...")

        if user_prompt:
            with st.spinner("Thinking..."):
                result = safe_llm_call(handle_user_query_dynamic, user_prompt, df, model_source, default={"response": "No response."})
            session_data["chat_history"].append({"user": user_prompt, "assistant": result})

        for msg in session_data["chat_history"][::-1]:
            with st.chat_message("user"):
                st.markdown(msg["user"])
            with st.chat_message("assistant"):
                st.markdown(msg["assistant"].get("response", msg["assistant"]))

    else:
        st.warning("No dataset loaded. Please upload a dataset first.")
