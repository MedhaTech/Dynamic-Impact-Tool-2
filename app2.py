# import os
# import json
# import streamlit as st
# from dotenv import load_dotenv
# import pandas as pd
# from io import BytesIO
# from utils.file_loader import load_data, clean_data
# from utils.chat_handler import handle_user_query_dynamic
# from utils.visualizer import (
#     visualize_from_llm_response,
#     visualize_comparison_overlay,
#     visualize_comparison_side_by_side
# )
# from utils.pdf_exporter import generate_pdf_report, export_to_pptx
# from utils.error_handler import safe_llm_call
# from utils.insight_suggester import (
#     generate_insight_suggestions,
#     generate_insights,
#     generate_comparison_insights
# )
# from utils.column_selector import get_important_columns
# from utils.llm_selector import get_llm

# load_dotenv()
# st.set_page_config(page_title="Dynamic Impact Tool", layout="wide")

# # Initialize session keys
# for key in ["df", "df1", "df2", "insights", "chat_history", "compare_chat", "insight_categories", "file_bytes", "file_name"]:
#     if key not in st.session_state:
#         st.session_state[key] = [] if "chat" in key else None

# # Sidebar
# with st.sidebar:
#     st.title("Dynamic Impact Tool")
#     section = st.radio("Navigate", ["Upload & Visualize", "Insights", "Compare Datasets", "Summary & Export"], key="sidebar_section")
#     model_source = st.selectbox("Model", ["groq", "ollama"], key="sidebar_model")

#     st.markdown("---")
#     if st.button("💾 Save Session"):
#         with open("saved_session.json", "w") as f:
#             json.dump(st.session_state._state.to_dict(), f)
#         st.toast("✅ Session saved successfully.")

#     if st.button("📂 Load Session"):
#         try:
#             with open("saved_session.json", "r") as f:
#                 saved_state = json.load(f)
#             for key, value in saved_state.items():
#                 st.session_state[key] = value
#             st.toast("✅ Session loaded successfully.")
#             st.experimental_rerun()
#         except Exception as e:
#             st.error(f"Failed to load session: {e}")

#     if st.button("🧹 Clear Session"):
#         for key in list(st.session_state.keys()):
#             del st.session_state[key]
#         st.experimental_rerun()

# # === Section 1: Upload & Visualize ===
# if section == "Upload & Visualize":
#     st.header("📥 Upload Dataset")

#     col1, col2 = st.columns(2)
#     uploaded_file = col1.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"], key="upload_main")
#     file_path = col2.text_input("Or Enter File Path", key="path_main")

#     if uploaded_file is not None:
#         st.session_state["file_bytes"] = uploaded_file.read()
#         st.session_state["file_name"] = uploaded_file.name
#         st.session_state["file_path_used"] = None

#     if file_path:
#         st.session_state["file_path_used"] = file_path.strip()
#         st.session_state["file_bytes"] = None
#         st.session_state["file_name"] = None

#     # Load from session
#     if st.session_state["df"] is None:
#         if st.session_state.get("file_bytes"):
#             with st.spinner("Loading uploaded file..."):
#                 file_like = BytesIO(st.session_state["file_bytes"])
#                 df, _ = load_data(file_like, st.session_state["file_name"])
#                 df = clean_data(df)
#                 st.session_state["df"] = df
#                 st.toast(f"✅ {st.session_state['file_name']} loaded successfully.")
#         elif st.session_state.get("file_path_used"):
#             try:
#                 with st.spinner("Loading file from path..."):
#                     file = open(st.session_state["file_path_used"], "rb")
#                     df, _ = load_data(file, st.session_state["file_name"])
#                     df = clean_data(df)
#                     st.session_state["df"] = df
#                     st.toast(f"✅ {st.session_state['file_path_used']} loaded successfully.")
#             except Exception as e:
#                 st.error(f"❌ File not found: {e}")
#     else:
#         df = st.session_state["df"]
#         st.info(f"✅ Dataset already loaded with {len(df)} rows and {len(df.columns)} columns.")

#         # === Dataset Preview ===
#     if "df" in st.session_state and st.session_state["df"] is not None:
#         df = st.session_state["df"]
#         sample_rows = st.slider("Preview Rows Limit (for display only)", 0, 100, 10, key="sample_rows_upload")
#         with st.expander("🔍 Dataset Preview"):
#             if sample_rows > 0:
#                 st.dataframe(df.head(sample_rows), use_container_width=True)
#             else:
#                 st.dataframe(df, use_container_width=True)

#         # === AI-SELECTED COLUMNS ===
#         st.markdown("## 🧠 AI-Selected + User-Selected Columns")
#         important_cols = get_important_columns(df.to_csv(index=False), model_source=model_source)

#         if important_cols:
#             st.success(f"AI selected {len(important_cols)} important columns.")
#             with st.expander("🔍 Preview AI-Selected Columns"):
#                 st.dataframe(df[important_cols].head(), use_container_width=True)
#         else:
#             st.warning("⚠️ AI failed to suggest important columns.")
#             important_cols = []

#         user_selected_cols = st.multiselect(
#             "✅ Select Additional Columns for Your Contextual Analysis",
#             options=df.columns.tolist(),
#             default=important_cols,
#             key="manual_col_select"
#         )

#         final_cols = list(set(important_cols + user_selected_cols))

#         if final_cols:
#             st.success(f"Total columns selected for analysis: {len(final_cols)}")
#             st.dataframe(df[final_cols].head(), use_container_width=True)
#         else:
#             st.warning("🚫 No columns selected. Please choose at least one.")

#         # === Visualization ===
#         st.markdown("## 📈 Visualization")
#         x_axis = st.selectbox("Select X-Axis", final_cols, key="x_axis")
#         y_axis = st.selectbox("Select Y-Axis", final_cols, key="y_axis")
#         chart_type = st.selectbox("Chart Type", ["bar", "line", "scatter", "box", "violin", "area", "pie"], key="chart_type")

#         if x_axis and y_axis and x_axis in df.columns and y_axis in df.columns:
#             try:
#                 llm_response = {"chart_type": chart_type, "x": x_axis, "y": y_axis, "group_by": None}
#                 fig, explanation = visualize_from_llm_response(df, f"{x_axis} vs {y_axis}", llm_response)
#                 if fig:
#                     st.plotly_chart(fig, use_container_width=True)
#                     st.caption(explanation)
#                 else:
#                     st.warning("No chart could be generated.")
#             except Exception as e:
#                 st.error(f"Visualization failed: {e}")
#         else:
#             st.info("Please select valid X and Y columns to generate visualization.")

#         # === Suggested Insights ===
#         st.markdown("## 🧠 Suggested Insights")
#         preview = df.head(10).to_csv(index=False)[:2048]

#         if "insight_suggestions" not in st.session_state or not st.session_state.get("insight_suggestions"):
#             try:
#                 suggestions = generate_insight_suggestions(preview, model_source)
#                 st.session_state["insight_suggestions"] = suggestions
#             except Exception as e:
#                 st.session_state["insight_suggestions"] = []
#                 st.warning(f"Insight suggestion failed: {e}")

#         titles = [s["title"] for s in st.session_state.get("insight_suggestions", [])]
#         if titles:
#             selected_title = st.selectbox("Select Insight to Generate", titles, key="insight_dropdown")
#             if st.button("Generate Insight"):
#                 try:
#                     insight_result = generate_insights(df, selected_title, model_source)
#                     st.session_state["insights"] = {"response": insight_result}
#                     st.success("Insight Generated")
#                     st.markdown(insight_result)
#                 except Exception as e:
#                     st.error(f"Insight generation failed: {str(e)}")
#         else:
#             st.warning("No insights available.")

#         # === Chat With Data ===
#         st.markdown("## 💬 Ask Your Data")
#         user_prompt = st.chat_input("Ask a question about your dataset...")
#         if user_prompt:
#             with st.spinner("Thinking..."):
#                 result = safe_llm_call(handle_user_query_dynamic, user_prompt, df, model_source, default={"response": "No response."})
#             st.session_state["chat_history"].append({"user": user_prompt, "assistant": result})

#         for msg in st.session_state["chat_history"][::-1]:
#             with st.chat_message("user"):
#                 st.markdown(msg["user"])
#             with st.chat_message("assistant"):
#                 st.markdown(msg["assistant"].get("response", msg["assistant"]))

# # # === Section 2: Insights ===


# import re

# def extract_json_from_response(response):
#     match = re.search(r"\[.*\]", response, re.DOTALL)
#     if match:
#         return match.group(0)
#     else:
#         raise ValueError("No JSON array found in response.")




# if section == "Insights":
    
#     st.markdown("""
#         <style>
#         .main-container {
#             display: flex;
#             justify-content: space-between;
#             align-items: flex-start;
#             padding: 20px;
#         }
#         .insight-content {
#             width: 70%;
#             padding: 20px;
#             background-color: #f9f9f9;
#             border-radius: 10px;
#         }
#         .insight-sidebar {
#             width: 28%;
#             padding: 20px;
#             background-color: #ffffff;
#             border-radius: 10px;
#             border: 1px solid #ddd;
#             max-height: 85vh;
#             overflow-y: auto;
#         }
#         </style>
#     """, unsafe_allow_html=True)


#     st.header("🧠 Insight Discovery Center")

#     col1, col2, col3 = st.columns([0.1, 0.7, 0.2])

#     with col2:
#         st.subheader("📋 Insight Result")
#         if st.session_state.get("selected_insight_result"):
#             st.markdown(st.session_state["selected_insight_result"])
#         else:
#             st.info("Select an insight question from the right to see results here.")

#     with col3:
#         st.subheader("🔍 Insight Categories")

#         if st.session_state.get("df") is not None:
#             df = st.session_state["df"]

#             if not st.session_state.get("insight_categories"):
#                 try:
#                     preview = df.head(10).to_csv(index=False)[:2048]
#                     llm = get_llm(model_source)

#                     prompt = f"""
#                     I have the following dataset preview:
#                     {preview}

#                     Please generate exactly 5 to 6 analytical insight categories based on this dataset.
#                     For each category, provide exactly 4 to 6 detailed analytical questions.

#                     ⚠️ IMPORTANT:
#                     Return the response strictly in this JSON format:
#                     [
#                         {{
#                             "title": "Category Name",
#                             "questions": ["Question 1", "Question 2", "Question 3"]
#                         }},
#                         ...
#                     ]

#                     ❗ Do not include any introduction, explanation, or extra text. Only return the JSON array.
#                     """

#                     response = llm(prompt)

#                     if hasattr(response, "content"):
#                         response = response.content

#                     json_string = extract_json_from_response(response)

#                     categories = json.loads(json_string)

#                     st.session_state["insight_categories"] = categories
#                     st.toast("✅ Categories loaded successfully.")

#                 except Exception as e:
#                     st.error(f"Insight suggestion failed: {e}")
#                     st.session_state["insight_categories"] = []

#             categories = st.session_state.get("insight_categories", [])

#             if categories:
#                 for idx, category in enumerate(categories):
#                     with st.expander(f"📂 {category['title']}"):
#                         for question in category.get("questions", []):
#                             if st.button(question, key=f"insight_{idx}_{question}"):
#                                 with st.spinner("Generating insight..."):
#                                     try:
#                                         result = generate_insights(df, question, model_source)
#                                         st.session_state["selected_insight_result"] = result
#                                         st.rerun()
#                                     except Exception as e:
#                                         st.error(f"Insight generation failed: {e}")
#             else:
#                 st.info("No categories available. Please upload a dataset in 'Upload & Visualize' tab.")
#         else:
#             st.warning("No dataset loaded. Please upload a dataset first in 'Upload & Visualize' tab.")

#     st.markdown("---")
#     user_prompt = st.chat_input("💬 Ask a question about your dataset...")
#     if user_prompt:
#         with st.spinner("Thinking..."):
#             result = safe_llm_call(handle_user_query_dynamic, user_prompt, st.session_state["df"], model_source, default={"response": "No response."})
#         st.session_state["chat_history"].append({"user": user_prompt, "assistant": result})

#     for msg in st.session_state["chat_history"][::-1]:
#         with st.chat_message("user"):
#             st.markdown(msg["user"])
#         with st.chat_message("assistant"):
#             st.markdown(msg["assistant"].get("response", msg["assistant"]))


# import os
# import json
# import re
# import streamlit as st
# from dotenv import load_dotenv
# import pandas as pd
# from io import BytesIO
# from utils.file_loader import load_data, clean_data
# from utils.chat_handler import handle_user_query_dynamic
# from utils.visualizer import (
#     visualize_from_llm_response,
#     visualize_comparison_overlay,
#     visualize_comparison_side_by_side
# )
# from utils.pdf_exporter import generate_pdf_report, export_to_pptx
# from utils.error_handler import safe_llm_call
# from utils.insight_suggester import (
#     generate_insight_suggestions,
#     generate_insights,
#     generate_comparison_insights
# )
# from utils.column_selector import get_important_columns
# from utils.llm_selector import get_llm

# load_dotenv()
# st.set_page_config(page_title="Dynamic Impact Tool", layout="wide")

# for key in ["df", "insight_categories", "selected_insight_results", "chat_history"]:
#     if key not in st.session_state:
#         st.session_state[key] = [] if key in ["selected_insight_results", "chat_history"] else None

# with st.sidebar:
#     st.title("Dynamic Impact Tool")
#     section = st.radio("Navigate", ["Upload & Visualize", "Insights"], key="sidebar_section")
#     model_source = st.selectbox("Model", ["groq", "ollama"], key="sidebar_model")

# # JSON Extraction Function
# def extract_json_from_response(response):
#     match = re.search(r"\[.*\]", response, re.DOTALL)
#     if match:
#         return match.group(0)
#     else:
#         raise ValueError("No JSON array found in response.")

# if section == "Upload & Visualize":
#     st.header("📥 Upload Dataset")

#     col1, col2 = st.columns(2)
#     uploaded_file = col1.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"], key="upload_main")

#     if uploaded_file is not None:
#         st.session_state["file_bytes"] = uploaded_file.read()
#         st.session_state["file_name"] = uploaded_file.name

#     if st.session_state.get("file_bytes") and st.session_state.get("file_name"):
#         file_like = BytesIO(st.session_state["file_bytes"])
#         df, _ = load_data(file_like, st.session_state["file_name"])
#         df = clean_data(df)
#         st.session_state["df"] = df
#         st.success(f"✅ {st.session_state['file_name']} loaded successfully.")

#     if st.session_state["df"] is not None:
#         df = st.session_state["df"]
#         st.write("### Dataset Preview", df.head())

# if section == "Insights":
#     st.markdown("""
#         <style>
#         .insight-sidebar {
#             width: 28%;
#             padding: 20px;
#             background-color: #ffffff;
#             border-radius: 12px;
#             border: 1px solid #ddd;
#             box-shadow: 0 4px 12px rgba(0,0,0,0.05);
#             max-height: 85vh;
#             overflow-y: auto;
#         }
#         .insight-sidebar::-webkit-scrollbar {
#             width: 6px;
#         }
#         .insight-sidebar::-webkit-scrollbar-thumb {
#             background-color: #ccc;
#             border-radius: 4px;
#         }
#         .insight-sidebar::-webkit-scrollbar-thumb:hover {
#             background-color: #999;
#         }
#         button[role="button"] {
#             background-color: #f1f1f1;
#             border: none;
#             border-radius: 8px;
#             padding: 8px 16px;
#             margin: 4px 0;
#             transition: background-color 0.3s ease;
#             font-weight: 500;
#         }
#         button[role="button"]:hover {
#             background-color: #e0e0e0;
#         }
#         </style>
#     """, unsafe_allow_html=True)

#     st.markdown("## 🧠 Insight Discovery Center")
#     st.markdown("---")

#     with st.container():
#         col1, col2 = st.columns([7, 3], gap="large")

#         with col1:
#             st.markdown("### 📋 Generated Insights")

#             if st.session_state.get("selected_insight_results"):
#                 for insight in st.session_state["selected_insight_results"][::-1]:
#                     with st.container(border=True):
#                         st.markdown(f"**🔍 {insight['question']}**")
#                         st.markdown(insight["result"])
#                         st.markdown("---")
#             else:
#                 st.info("Please select an insight question from the right to view the results.")

#         with col2:
#             st.markdown("## 🔍 Insight Categories")

#             if st.session_state.get("insight_categories"):
#                 for idx, category in enumerate(st.session_state["insight_categories"]):
#                     with st.expander(f"📂 {category['title']}", expanded=False):
#                         for question in category.get("questions", []):
#                             if st.button(f"🔎 {question}", key=f"insight_{idx}_{question}"):
#                                 with st.spinner("Generating insight..."):
#                                     try:
#                                         result = generate_insights(st.session_state["df"], question, model_source)

#                                         st.session_state["selected_insight_results"].append({
#                                             "question": question,
#                                             "result": result
#                                         })

#                                         st.rerun()
#                                     except Exception as e:
#                                         st.error(f"Insight generation failed: {e}")
#             else:
#                 if st.session_state.get("df") is not None:
#                     try:
#                         preview = st.session_state["df"].head(10).to_csv(index=False)[:2048]
#                         llm = get_llm(model_source)

#                         prompt = f"""
#                         I have the following dataset preview:
#                         {preview}

#                         Please generate exactly 5 to 6 analytical insight categories based on this dataset.
#                         For each category, provide exactly 4 to 6 detailed analytical questions.

#                         ⚠️ IMPORTANT:
#                         Return the response strictly in this JSON format:
#                         [
#                             {{
#                                 "title": "Category Name",
#                                 "questions": ["Question 1", "Question 2", "Question 3"]
#                             }},
#                             ...
#                         ]

#                         ❗ Do not include any introduction, explanation, or extra text. Only return the JSON array.
#                         """

#                         response = llm(prompt)

#                         if hasattr(response, "content"):
#                             response = response.content

#                         st.write("🔍 LLM Raw Response:", response)

#                         json_string = extract_json_from_response(response)

#                         categories = json.loads(json_string)

#                         st.session_state["insight_categories"] = categories
#                         st.toast("✅ Categories loaded successfully.")

#                         st.rerun()
#                     except Exception as e:
#                         st.error(f"Insight suggestion failed: {e}")
#                         st.session_state["insight_categories"] = []
#                 else:
#                     st.warning("No dataset loaded. Please upload a dataset first.")

#     st.markdown("---")

    # user_prompt = st.chat_input("💬 Ask a question about your dataset...")
    # if user_prompt:
    #     with st.spinner("Thinking..."):
    #         result = safe_llm_call(handle_user_query_dynamic, user_prompt, st.session_state["df"], model_source, default={"response": "No response."})
    #     st.session_state["chat_history"].append({"user": user_prompt, "assistant": result})

    # for msg in st.session_state["chat_history"][::-1]:
    #     with st.chat_message("user"):
    #         st.markdown(msg["user"])
    #     with st.chat_message("assistant"):
    #         st.markdown(msg["assistant"].get("response", msg["assistant"]))


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

# Initialize session keys
for key in ["df", "df1", "df2", "insights", "chat_history", "compare_chat", "insight_categories", "file_bytes", "file_name", "selected_insight_results"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ["chat_history", "compare_chat", "selected_insight_results"] else None

# Sidebar
with st.sidebar:
    st.title("Dynamic Impact Tool")
    section = st.radio("Navigate", ["Upload & Visualize", "Insights", "Compare Datasets", "Summary & Export"], key="sidebar_section")
    model_source = st.selectbox("Model", ["groq", "ollama"], key="sidebar_model")

# === Section 1: Upload & Visualize ===
if section == "Upload & Visualize":
    st.header("📥 Upload Dataset")

    col1, col2 = st.columns(2)
    uploaded_file = col1.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"], key="upload_main")
    file_path = col2.text_input("Or Enter File Path", key="path_main")

    if uploaded_file is not None:
        st.session_state["file_bytes"] = uploaded_file.read()
        st.session_state["file_name"] = uploaded_file.name
        st.session_state["file_path_used"] = None

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
                st.toast(f"✅ {st.session_state['file_name']} loaded successfully.")
        elif st.session_state.get("file_path_used"):
            try:
                with st.spinner("Loading file from path..."):
                    file = open(st.session_state["file_path_used"], "rb")
                    df, _ = load_data(file, st.session_state["file_name"])
                    df = clean_data(df)
                    st.session_state["df"] = df
                    st.toast(f"✅ {st.session_state['file_path_used']} loaded successfully.")
            except Exception as e:
                st.error(f"❌ File not found: {e}")
    else:
        df = st.session_state["df"]
        st.info(f"✅ Dataset already loaded with {len(df)} rows and {len(df.columns)} columns.")

    if "df" in st.session_state and st.session_state["df"] is not None:
        df = st.session_state["df"]
        sample_rows = st.slider("Preview Rows Limit (for display only)", 0, 100, 10, key="sample_rows_upload")
        with st.expander("🔍 Dataset Preview"):
            if sample_rows > 0:
                st.dataframe(df.head(sample_rows), use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)

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
        else:
            st.warning("🚫 No columns selected. Please choose at least one.")

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
           st.session_state["chat_history"].append({"user": user_prompt, "assistant": result})

        for msg in st.session_state["chat_history"][::-1]:
           with st.chat_message("user"):
            st.markdown(msg["user"])
           with st.chat_message("assistant"):
            st.markdown(msg["assistant"].get("response", msg["assistant"]))

# === Section 2: Insights ===
if section == "Insights":
    st.markdown("""
        <style>
        .insight-sidebar {
            width: 28%;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid #ddd;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            max-height: 85vh;
            overflow-y: auto;
        }
        .insight-sidebar::-webkit-scrollbar {
            width: 6px;
        }
        .insight-sidebar::-webkit-scrollbar-thumb {
            background-color: #ccc;
            border-radius: 4px;
        }
        .insight-sidebar::-webkit-scrollbar-thumb:hover {
            background-color: #999;
        }
        button[role="button"] {
            background-color: #f1f1f1;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            margin: 4px 0;
            transition: background-color 0.3s ease;
            font-weight: 500;
        }
        button[role="button"]:hover {
            background-color: #e0e0e0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 🧠 Insight Discovery Center")
    st.markdown("---")

    with st.container():
        col1, col2 = st.columns([7, 3], gap="large")

        with col1:
            st.markdown("### 📋 Generated Insights")

            if st.session_state.get("selected_insight_results"):
                for insight in st.session_state["selected_insight_results"][::-1]:
                    with st.container(border=True):
                        st.markdown(f"**🔍 {insight['question']}**")
                        st.markdown(insight["result"])
                        st.markdown("---")
            else:
                st.info("Please select an insight question from the right to view the results.")

        with col2:
            st.markdown("## 🔍 Insight Categories")

            if st.session_state.get("insight_categories"):
                for idx, category in enumerate(st.session_state["insight_categories"]):
                    with st.expander(f"📂 {category['title']}", expanded=False):
                        for question in category.get("questions", []):
                            if st.button(f"🔎 {question}", key=f"insight_{idx}_{question}"):
                                with st.spinner("Generating insight..."):
                                    try:
                                        result = generate_insights(st.session_state["df"], question, model_source)
                                        st.session_state["selected_insight_results"].append({"question": question, "result": result})
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Insight generation failed: {e}")
            else:
                if st.session_state.get("df") is not None:
                    try:
                        preview = st.session_state["df"].head(10).to_csv(index=False)[:2048]
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

                        st.session_state["insight_categories"] = categories
                        st.toast("✅ Categories loaded successfully.")

                        st.rerun()
                    except Exception as e:
                        st.error(f"Insight suggestion failed: {e}")
                        st.session_state["insight_categories"] = []
                else:
                    st.warning("No dataset loaded. Please upload a dataset first.")

    st.markdown("---")

    user_prompt = st.chat_input("💬 Ask a question about your dataset...")
    if user_prompt:
        with st.spinner("Thinking..."):
            result = safe_llm_call(handle_user_query_dynamic, user_prompt, st.session_state["df"], model_source, default={"response": "No response."})
        st.session_state["chat_history"].append({"user": user_prompt, "assistant": result})

    for msg in st.session_state["chat_history"][::-1]:
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant"):
            st.markdown(msg["assistant"].get("response", msg["assistant"]))





# === Section 3: Compare Datasets ===
if section == "Compare Datasets":
    st.header("📊 Compare Datasets")

    col1, col2 = st.columns(2)

    uploaded_file1 = col1.file_uploader("Upload Dataset 1", type=["csv", "xlsx", "json"], key="upload_1")
    file_path1 = col1.text_input("Or Enter Path for Dataset 1", key="path_1")

    uploaded_file2 = col2.file_uploader("Upload Dataset 2", type=["csv", "xlsx", "json"], key="upload_2")
    file_path2 = col2.text_input("Or Enter Path for Dataset 2", key="path_2")

    # Save file contents for Dataset 1
    if uploaded_file1 is not None:
        st.session_state["file1_bytes"] = uploaded_file1.read()
        st.session_state["file1_name"] = uploaded_file1.name
        st.session_state["file1_path"] = None

    if file_path1:
        st.session_state["file1_path"] = file_path1.strip()
        st.session_state["file1_bytes"] = None
        st.session_state["file1_name"] = None

    # Save file contents for Dataset 2
    if uploaded_file2 is not None:
        st.session_state["file2_bytes"] = uploaded_file2.read()
        st.session_state["file2_name"] = uploaded_file2.name
        st.session_state["file2_path"] = None

    if file_path2:
        st.session_state["file2_path"] = file_path2.strip()
        st.session_state["file2_bytes"] = None
        st.session_state["file2_name"] = None

    # Load Dataset 1
    if st.session_state["df1"] is None:
        if st.session_state.get("file1_bytes"):
            with st.spinner("Loading Dataset 1..."):
                file_like1 = BytesIO(st.session_state["file1_bytes"])
                df1, _ = load_data(file_like1, st.session_state["file1_name"])
                df1 = clean_data(df1)
                st.session_state["df1"] = df1
                st.toast(f"✅ {st.session_state['file1_name']} loaded successfully.")
        elif st.session_state.get("file1_path"):
            try:
                with st.spinner("Loading Dataset 1 from path..."):
                    file1 = open(st.session_state["file1_path"], "rb")
                    df1, _ = load_data(file1, st.session_state["file1_name"])
                    df1 = clean_data(df1)
                    st.session_state["df1"] = df1
                    st.toast(f"✅ {st.session_state['file1_path']} loaded successfully.")
            except Exception as e:
                st.error(f"File not found: {e}")

    # Load Dataset 2
    if st.session_state["df2"] is None:
        if st.session_state.get("file2_bytes"):
            with st.spinner("Loading Dataset 2..."):
                file_like2 = BytesIO(st.session_state["file2_bytes"])
                df2, _ = load_data(file_like2, st.session_state["file2_name"])
                df2 = clean_data(df2)
                st.session_state["df2"] = df2
                st.toast(f"✅ {st.session_state['file2_name']} loaded successfully.")
        elif st.session_state.get("file2_path"):
            try:
                with st.spinner("Loading Dataset 2 from path..."):
                    file2 = open(st.session_state["file2_path"], "rb")
                    df2, _ = load_data(file2, st.session_state["file2_name"])
                    df2 = clean_data(df2)
                    st.session_state["df2"] = df2
                    st.toast(f"✅ {st.session_state['file2_path']} loaded successfully.")
            except Exception as e:
                st.error(f"File not found: {e}")

    # Proceed if both datasets are loaded
    if st.session_state["df1"] is not None and st.session_state["df2"] is not None:
        df1 = st.session_state["df1"]
        df2 = st.session_state["df2"]

        df1.columns = [col.strip().lower() for col in df1.columns]
        df2.columns = [col.strip().lower() for col in df2.columns]

        st.success("✅ Both datasets loaded successfully.")

        # Dataset Previews
        st.subheader("📋 Dataset Previews")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Dataset 1")
            st.dataframe(df1.head(), use_container_width=True)
        with col2:
            st.markdown("#### Dataset 2")
            st.dataframe(df2.head(), use_container_width=True)

        # AI + User Column Selection
        st.subheader("🧠 AI + User Column Selector")
        ai_cols1 = get_important_columns(df1.to_csv(index=False), model_source)
        ai_cols1 = [col.strip().lower() for col in ai_cols1]
        matched_in_df2 = [col for col in ai_cols1 if col in df2.columns]
        missing_in_df2 = list(set(ai_cols1) - set(matched_in_df2))
        st.info(f"⚠️ Missing in Dataset 2: {', '.join(missing_in_df2) if missing_in_df2 else 'None'}")

        col1, col2 = st.columns(2)
        with col1:
            user_cols1 = st.multiselect("✅ Select Additional Columns from Dataset 1", df1.columns.tolist(), default=ai_cols1, key="manual_cols_1")
            final_cols1 = list(set(ai_cols1 + user_cols1))
            st.success(f"Selected Columns in Dataset 1: {final_cols1}")
        with col2:
            final_cols2 = [col for col in final_cols1 if col in df2.columns]
            st.success(f"Matched Columns in Dataset 2: {final_cols2}")
            if not final_cols2:
                st.warning("🚫 No common columns between selected Dataset 1 columns and Dataset 2.")

        df1 = df1[final_cols1] if final_cols1 else df1
        df2 = df2[final_cols2] if final_cols2 else df2

        # Manual Comparison Visualization
        st.subheader("📈 Manual Comparison Visualization")
        common_cols = list(set(df1.columns).intersection(set(df2.columns)))

        if not common_cols:
            st.warning("⚠️ No common columns to visualize.")
        else:
            x_axis = st.selectbox("📌 Select X-Axis", common_cols, key="compare_x_axis")
            y_axis = st.selectbox("📌 Select Y-Axis", common_cols, key="compare_y_axis")
            layout = st.radio("🧩 Layout", ["Overlay", "Side-by-Side"], horizontal=True, key="compare_layout")
            chart_type = st.selectbox("📈 Chart Type", ["bar", "line", "scatter"], key="compare_chart")

            if layout == "Overlay":
                fig, explanation = visualize_comparison_overlay(df1, df2, x_axis, y_axis, "Dataset 1", "Dataset 2", chart_type)
                st.plotly_chart(fig, use_container_width=True)
                st.caption(explanation)
            else:
                fig1, fig2 = visualize_comparison_side_by_side(df1, df2, x_axis, y_axis, chart_type)
                col1, col2 = st.columns(2)
                col1.plotly_chart(fig1, use_container_width=True)
                col2.plotly_chart(fig2, use_container_width=True)

        # AI-Suggested Comparison Insights
        st.subheader("🧠 Suggested Comparison Insights")
        merged_df = pd.concat([
            df1.assign(dataset="Dataset 1"),
            df2.assign(dataset="Dataset 2")
        ])
        preview = merged_df.head(10).to_csv(index=False)[:2048]

        if "compare_insight_suggestions" not in st.session_state or not st.session_state.get("compare_insight_suggestions"):
            try:
                titles = generate_insight_suggestions(preview, model_source)
                st.session_state["compare_insight_suggestions"] = titles
            except Exception as e:
                st.warning(f"Insight suggestion failed: {e}")
                st.session_state["compare_insight_suggestions"] = []

        titles = [t["title"] for t in st.session_state.get("compare_insight_suggestions", [])]
        if titles:
            selected_compare_title = st.selectbox("🧠 Select Insight to Generate", titles, key="selected_comparison_dropdown")

            if st.button("Generate Comparison Insight", key="dynamic_comparison_insight"):
                try:
                    insight_result = generate_insights(merged_df, selected_compare_title, model_source)
                    st.success("Insight Generated")
                    st.markdown(insight_result)
                    st.session_state["insights"] = {"response": insight_result}
                except Exception as e:
                    st.error(f"Insight generation failed: {str(e)}")
        else:
            st.warning("No insights available to suggest.")

        # Chat with Comparison Datasets
        st.subheader("💬 Chat About This Comparison")
        compare_prompt = st.chat_input("Ask a question about the comparison...")
        if compare_prompt:
            with st.spinner("Thinking..."):
                result = safe_llm_call(handle_user_query_dynamic, compare_prompt, merged_df, model_source, default={"response": "No response."})
            st.session_state["compare_chat"].append({"user": compare_prompt, "assistant": result})

        for msg in st.session_state["compare_chat"][::-1]:
            with st.chat_message("user"):
                st.markdown(msg["user"])
            with st.chat_message("assistant"):
                st.markdown(msg["assistant"].get("response", msg["assistant"]))
    else:
        st.warning("⚠️ Please upload or enter a valid path for both datasets.")


# === Section 4: Summary & Export ===
if section == "Summary & Export":
    st.header("📦 Summary & Export")

    insights = st.session_state.get("insights", "No insights generated yet.")
    chat_logs = st.session_state.get("chat_history", []) + st.session_state.get("compare_chat", [])

    # --- Insight Summary ---
    st.subheader("Insight Summary")
    if insights:
        if isinstance(insights, dict) and "response" in insights:
            st.markdown(insights["response"])
        else:
            st.markdown(insights)
    else:
        st.warning("No insights to display.")

    # --- Chat History ---
    if chat_logs:
        st.subheader("Chat History")
        for msg in chat_logs[::-1]:
            with st.chat_message("user"):
                st.markdown(msg["user"])
            with st.chat_message("assistant"):
                st.markdown(msg["assistant"].get("response", msg["assistant"]))
    else:
        st.info("No chat history to display.")

    insights_summary = ""
    if st.session_state["insights"]:
        if isinstance(st.session_state["insights"], dict) and "response" in st.session_state["insights"]:
            insights_summary = st.session_state["insights"]["response"]
        else:
            insights_summary = str(st.session_state["insights"])

    all_chat_logs = st.session_state["chat_history"] + st.session_state["compare_chat"]

    # --- Export Buttons ---
    st.subheader("📁 Export Report")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Export PDF"):
            try:
                pdf_path = generate_pdf_report(insights_summary, all_chat_logs)
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF", f, file_name="summary.pdf")
            except Exception as e:
                st.error(f"Failed to export PDF: {e}")

    with col2:
        if st.button("📊 Export PPTX"):
            try:
                pptx_path = export_to_pptx(insights_summary, all_chat_logs)
                with open(pptx_path, "rb") as f:
                    st.download_button("Download PPTX", f, file_name="summary.pptx")
            except Exception as e:
                st.error(f"Failed to export PPTX: {e}")
