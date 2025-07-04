# import streamlit as st
# from io import BytesIO
# from utils.file_loader import load_data, clean_data
# from utils.column_selector import get_important_columns
# from utils.visualizer import visualize_from_llm_response
# from utils.chat_handler import handle_user_query_dynamic
# from utils.pdf_exporter import generate_pdf_report, export_to_pptx
# from utils.insight_suggester import generate_insights, generate_insight_suggestions
# from utils.llm_selector import get_llm
# from utils.error_handler import safe_llm_call
# import pandas as pd
# import json
# import re

# st.set_page_config(page_title="Dynamic Impact Tool", layout="wide")

# # ==================== SESSION INITIALIZATION ==================== #
# if "dataset_sessions" not in st.session_state:
#     st.session_state["dataset_sessions"] = {}
# if "current_session" not in st.session_state:
#     st.session_state["current_session"] = None
# if "compare_sessions" not in st.session_state:
#     st.session_state["compare_sessions"] = {}
# if "current_compare" not in st.session_state:
#     st.session_state["current_compare"] = None

# # ==================== SIDEBAR ==================== #
# with st.sidebar:
#     st.title("Dynamic Impact Tool")
#     model_source = st.selectbox("Model", ["groq", "ollama"], key="sidebar_model")


#     st.markdown("## 📥 Upload Dataset")
#     uploaded_file = st.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"], key="sidebar_upload")
#     file_path = st.text_input("Or Enter File Path")

#     if st.button("Upload Dataset"):
#         if uploaded_file is not None:
#             file_name = uploaded_file.name
#             file_bytes = uploaded_file.read()
#             file_like = BytesIO(file_bytes)
#             df, _ = load_data(file_like, file_name)
#             df = clean_data(df)

#             if file_name not in st.session_state["dataset_sessions"]:
#                 st.session_state["dataset_sessions"][file_name] = {
#                     "df": df,
#                     "chat_history": [],
#                     "insight_categories": [],
#                     "selected_insight_results": [],
#                     "visualization_history": [],
#                     "column_selection": []
#                 }

#             st.session_state["current_session"] = file_name
#             st.toast(f"✅ {file_name} uploaded successfully.")
#             st.rerun()

#         elif file_path:
#             try:
#                 file_name = file_path.split("/")[-1]
#                 file = open(file_path, "rb")
#                 df, _ = load_data(file, file_name)
#                 df = clean_data(df)

#                 if file_name not in st.session_state["dataset_sessions"]:
#                     st.session_state["dataset_sessions"][file_name] = {
#                         "df": df,
#                         "chat_history": [],
#                         "insight_categories": [],
#                         "selected_insight_results": [],
#                         "visualization_history": [],
#                         "column_selection": []
#                     }

#                 st.session_state["current_session"] = file_name
#                 st.toast(f"✅ {file_name} uploaded successfully.")
#                 st.rerun()

#             except Exception as e:
#                 st.error(f"File not found: {e}")
#         else:
#             st.warning("Please upload a file or enter a valid path.")

#     # ================= Dataset History ================= #
#     st.markdown("## 🗂️ Dataset History")
#     dataset_names = list(st.session_state["dataset_sessions"].keys())

#     if dataset_names:
#         selected_dataset = st.radio("Select Dataset Session", dataset_names,
#                                     index=dataset_names.index(st.session_state["current_session"]) if st.session_state["current_session"] else 0)

#         if selected_dataset != st.session_state["current_session"]:
#             st.session_state["current_session"] = selected_dataset
#             st.toast(f"✅ Switched to {selected_dataset}")
#             st.rerun()

#         st.markdown("### ✏️ Rename Current Dataset")
#         new_name = st.text_input("Enter New Name", placeholder="New dataset name...")
#         if st.button("Rename Dataset"):
#             if new_name and new_name not in st.session_state["dataset_sessions"]:
#                 st.session_state["dataset_sessions"][new_name] = st.session_state["dataset_sessions"].pop(st.session_state["current_session"])
#                 st.session_state["current_session"] = new_name
#                 st.toast(f"✅ Dataset renamed to {new_name}")
#                 st.rerun()
#             else:
#                 st.warning("Please enter a unique dataset name.")

#     else:
#         st.info("No datasets uploaded yet.")

#     st.markdown("---")
#     if st.button("🧹 Clear All Sessions"):
#         st.session_state["dataset_sessions"] = {}
#         st.session_state["current_session"] = None
#         st.experimental_rerun()

# # ==================== MAIN TABS ==================== #
# tab1, tab2, tab3 = st.tabs(["📊 Upload & Visualize", "🧠 Insights", "🔁 Compare Datasets"])

# # ==================== TAB 1: Upload & Visualize ==================== #
# with tab1:
#     st.header("📊 Upload & Visualize")

#     if st.session_state["current_session"]:
#         session = st.session_state["dataset_sessions"][st.session_state["current_session"]]
#         df = session["df"]

#         export_col1, export_col2 = st.columns([0.8, 0.2])
#         with export_col2:
#             st.markdown("#### Export Report")
#             if st.button("📄 Export PDF", key="export_pdf_visualize"):
#                 pdf_path = generate_pdf_report(session)
#                 with open(pdf_path, "rb") as f:
#                     st.download_button("Download PDF", f, file_name="visualization_report.pdf")
#             if st.button("📊 Export PPTX", key="export_ppt_visualize"):
#                 pptx_path = export_to_pptx(session)
#                 with open(pptx_path, "rb") as f:
#                     st.download_button("Download PPTX", f, file_name="visualization_report.pptx")

#         st.subheader("📋 Dataset Summary")
#         st.write(f"Total Rows: {df.shape[0]}")
#         st.write(f"Total Columns: {df.shape[1]}")

#         st.subheader("👁 Dataset Preview")
#         sample_rows = st.slider("Preview Rows Limit", 0, 100, 10, key="sample_rows_visualize")
#         st.dataframe(df.head(sample_rows), use_container_width=True)

#         st.subheader("🗂 Column Selection")
#         important_cols = get_important_columns(df.to_csv(index=False))
#         user_selected_cols = st.multiselect("Select Additional Columns", df.columns.tolist(), default=important_cols)

#         final_cols = list(set(important_cols + user_selected_cols))
#         session["column_selection"] = final_cols

#         st.write(f"Selected Columns: {final_cols}")
#         st.dataframe(df[final_cols].head(), use_container_width=True)

#         st.subheader("📈 Visualizations")
#         x_axis = st.selectbox("Select X-Axis", final_cols)
#         y_axis = st.selectbox("Select Y-Axis", final_cols)
#         chart_type = st.selectbox("Chart Type", ["bar", "line", "scatter", "box", "violin", "area", "pie"])

#         if x_axis and y_axis:
#             try:
#                 llm_response = {"chart_type": chart_type, "x": x_axis, "y": y_axis, "group_by": None}
#                 fig, explanation = visualize_from_llm_response(df, f"{x_axis} vs {y_axis}", llm_response)
#                 if fig:
#                     st.plotly_chart(fig, use_container_width=True)
#                     session["visualization_history"].append(f"{chart_type} chart: {x_axis} vs {y_axis}")
#                     st.caption(explanation)
#             except Exception as e:
#                 st.error(f"Visualization failed: {e}")

#         st.markdown("## 💬 Ask Your Data")

#         user_prompt = st.chat_input("💬 Ask a question about your dataset...")
#         if user_prompt:
           
#            with st.spinner("Thinking..."):
             
#               result = safe_llm_call(handle_user_query_dynamic, user_prompt, st.session_state["df"], model_source, default={"response": "No response."})
#            st.session_state["chat_history"].append({"user": user_prompt, "assistant": result})

#         for msg in st.session_state["chat_history"][::-1]:
#            with st.chat_message("user"):
#             st.markdown(msg["user"])
#            with st.chat_message("assistant"):
#             st.markdown(msg["assistant"].get("response", msg["assistant"]))

        

# # ==================== TAB 2: Insights ==================== #
# with tab2:
#     st.header("🧠 Insights")

#     if st.session_state["current_session"]:
#         session = st.session_state["dataset_sessions"][st.session_state["current_session"]]
#         df = session["df"]

#         export_col1, export_col2 = st.columns([0.8, 0.2])
#         with export_col2:
#             st.markdown("#### Export Report")
#             if st.button("📄 Export PDF", key="export_pdf_insight"):
#                 pdf_path = generate_pdf_report(session)
#                 with open(pdf_path, "rb") as f:
#                     st.download_button("Download PDF", f, file_name="insight_report.pdf")
#             if st.button("📊 Export PPTX", key="export_ppt_insight"):
#                 pptx_path = export_to_pptx(session)
#                 with open(pptx_path, "rb") as f:
#                     st.download_button("Download PPTX", f, file_name="insight_report.pptx")

#         # Display previous insights
#         st.subheader("📋 Generated Insights")
#         for insight in session["selected_insight_results"][::-1]:
#             with st.container(border=True):
#                 st.markdown(f"**🔍 {insight['question']}**")
#                 st.markdown(insight["result"])
#                 st.markdown("---")

#         # Load categories if not loaded
#         if not session["insight_categories"]:
#             try:
#                 preview = df.head(10).to_csv(index=False)[:2048]
#                 llm = get_llm("groq")
#                 prompt = f"""
#                 I have the following dataset preview:
#                 {preview}

#                 Please generate 5-6 analytical insight categories with 4-6 detailed questions each.
#                 Return strictly in JSON format:
#                 [
#                     {{"title": "Category Name", "questions": ["Question 1", "Question 2", "Question 3"]}},
#                     ...
#                 ]
#                 """
#                 response = llm(prompt)
#                 if hasattr(response, "content"):
#                     response = response.content
#                 json_string = re.search(r"\[.*\]", response, re.DOTALL).group(0)
#                 categories = json.loads(json_string)
#                 session["insight_categories"] = categories
#                 st.toast("✅ Categories loaded successfully.")
#                 st.rerun()
#             except Exception as e:
#                 st.error(f"Insight suggestion failed: {e}")
#                 session["insight_categories"] = []

#         st.subheader("🔍 Insight Categories")
#         for idx, category in enumerate(session["insight_categories"]):
#             with st.expander(f"📂 {category['title']}"):
#                 for question in category["questions"]:
#                     if st.button(f"🔎 {question}", key=f"insight_{idx}_{question}"):
#                         try:
#                             result = generate_insights(df, question, "groq")
#                             session["selected_insight_results"].append({"question": question, "result": result})
#                             st.rerun()
#                         except Exception as e:
#                             st.error(f"Insight generation failed: {e}")


#         st.markdown("## 💬 Ask Your Data")

#         user_prompt = st.chat_input("💬 Ask a question about your dataset...")
#         if user_prompt:
           
#            with st.spinner("Thinking..."):
             
#               result = safe_llm_call(handle_user_query_dynamic, user_prompt, st.session_state["df"], model_source, default={"response": "No response."})
#            st.session_state["chat_history"].append({"user": user_prompt, "assistant": result})

#         for msg in st.session_state["chat_history"][::-1]:
#            with st.chat_message("user"):
#             st.markdown(msg["user"])
#            with st.chat_message("assistant"):
#             st.markdown(msg["assistant"].get("response", msg["assistant"]))

# # ==================== TAB 3: Compare Datasets ==================== #
# # You can directly paste your existing Compare Datasets logic here
# with tab3:
#     st.header("🔁 Compare Datasets")

#     # Export options for comparison
#     export_col1, export_col2 = st.columns([0.8, 0.2])
#     with export_col2:
#         st.markdown("#### Export Report")
#         if st.button("📄 Export PDF", key="export_pdf_compare"):
#             if "compare_sessions" in st.session_state:
#                 compare_data = st.session_state["compare_sessions"]
#                 pdf_path = generate_pdf_report(compare_data)
#                 with open(pdf_path, "rb") as f:
#                     st.download_button("Download PDF", f, file_name="comparison_report.pdf")

#         if st.button("📊 Export PPTX", key="export_ppt_compare"):
#             if "compare_sessions" in st.session_state:
#                 compare_data = st.session_state["compare_sessions"]
#                 pptx_path = export_to_pptx(compare_data)
#                 with open(pptx_path, "rb") as f:
#                     st.download_button("Download PPTX", f, file_name="comparison_report.pptx")

#     st.subheader("📤 Upload Files for Comparison")
#     col1, col2 = st.columns(2)

#     uploaded_file1 = col1.file_uploader("Upload Dataset 1", type=["csv", "xlsx", "json"], key="compare_upload_1")
#     uploaded_file2 = col2.file_uploader("Upload Dataset 2", type=["csv", "xlsx", "json"], key="compare_upload_2")

#     file_path1 = col1.text_input("Or Enter Path for Dataset 1")
#     file_path2 = col2.text_input("Or Enter Path for Dataset 2")

#     if "compare_sessions" not in st.session_state:
#         st.session_state["compare_sessions"] = {}

#     if "compare_history" not in st.session_state:
#         st.session_state["compare_history"] = []

#     if st.button("Upload and Compare"):
#         try:
#             if uploaded_file1 is not None and uploaded_file2 is not None:
#                 file_name1 = uploaded_file1.name
#                 file_name2 = uploaded_file2.name
#                 df1, _ = load_data(BytesIO(uploaded_file1.read()), file_name1)
#                 df2, _ = load_data(BytesIO(uploaded_file2.read()), file_name2)

#             elif file_path1 and file_path2:
#                 file_name1 = file_path1.split("/")[-1]
#                 file_name2 = file_path2.split("/")[-1]
#                 df1, _ = load_data(open(file_path1, "rb"), file_name1)
#                 df2, _ = load_data(open(file_path2, "rb"), file_name2)

#             else:
#                 st.warning("Please upload both datasets or provide file paths.")
#                 st.stop()

#             df1 = clean_data(df1)
#             df2 = clean_data(df2)

#             compare_key = f"{file_name1} vs {file_name2}"
#             st.session_state["compare_sessions"][compare_key] = {
#                 "df1": df1,
#                 "df2": df2,
#                 "chat_history": [],
#                 "insights": [],
#                 "visualization_history": []
#             }
#             st.session_state["current_compare"] = compare_key
#             st.session_state["compare_history"].append(compare_key)
#             st.toast(f"✅ Comparison loaded: {compare_key}")
#             st.rerun()

#         except Exception as e:
#             st.error(f"Comparison upload failed: {e}")

#     if "current_compare" in st.session_state:
#         compare_key = st.session_state["current_compare"]
#         compare_session = st.session_state["compare_sessions"][compare_key]

#         df1 = compare_session["df1"]
#         df2 = compare_session["df2"]

#         st.success(f"Currently Comparing: {compare_key}")

#         st.subheader("📋 Dataset Previews")
#         col1, col2 = st.columns(2)
#         with col1:
#             st.markdown("#### Dataset 1")
#             st.dataframe(df1.head(), use_container_width=True)
#         with col2:
#             st.markdown("#### Dataset 2")
#             st.dataframe(df2.head(), use_container_width=True)

#         st.subheader("🗂 Column Selection for Comparison")
#         common_cols = list(set(df1.columns).intersection(set(df2.columns)))
#         if not common_cols:
#             st.warning("No common columns found between both datasets.")
#             st.stop()

#         x_axis = st.selectbox("Select X-Axis for Comparison", common_cols, key="compare_x_axis")
#         y_axis = st.selectbox("Select Y-Axis for Comparison", common_cols, key="compare_y_axis")
#         chart_type = st.selectbox("Chart Type", ["bar", "line", "scatter"], key="compare_chart")
#         layout = st.radio("Layout", ["Overlay", "Side-by-Side"], horizontal=True, key="compare_layout")

#         if x_axis and y_axis:
#             from utils.visualizer import visualize_comparison_overlay, visualize_comparison_side_by_side
#             try:
#                 if layout == "Overlay":
#                     fig, explanation = visualize_comparison_overlay(df1, df2, x_axis, y_axis, "Dataset 1", "Dataset 2", chart_type)
#                     st.plotly_chart(fig, use_container_width=True)
#                     st.caption(explanation)
#                     compare_session["visualization_history"].append(f"{chart_type} chart: {x_axis} vs {y_axis} (Overlay)")
#                 else:
#                     fig1, fig2 = visualize_comparison_side_by_side(df1, df2, x_axis, y_axis, chart_type)
#                     col1, col2 = st.columns(2)
#                     col1.plotly_chart(fig1, use_container_width=True)
#                     col2.plotly_chart(fig2, use_container_width=True)
#                     compare_session["visualization_history"].append(f"{chart_type} chart: {x_axis} vs {y_axis} (Side-by-Side)")

#             except Exception as e:
#                 st.error(f"Comparison visualization failed: {e}")

#         st.subheader("🧠 Suggested Comparison Insights")
#         merged_df = pd.concat([df1.assign(dataset="Dataset 1"), df2.assign(dataset="Dataset 2")])
#         preview = merged_df.head(10).to_csv(index=False)[:2048]

#         if "compare_insight_suggestions" not in compare_session:
#             from utils.insight_suggester import generate_insight_suggestions
#             try:
#                 suggestions = generate_insight_suggestions(preview, "groq")
#                 compare_session["compare_insight_suggestions"] = suggestions
#             except Exception as e:
#                 st.warning(f"Insight suggestion failed: {e}")
#                 compare_session["compare_insight_suggestions"] = []

#         titles = [s["title"] for s in compare_session.get("compare_insight_suggestions", [])]
#         if titles:
#             selected_title = st.selectbox("Select Comparison Insight", titles, key="selected_comparison_dropdown")
#             if st.button("Generate Comparison Insight", key="generate_comparison_insight"):
#                 try:
#                     from utils.insight_suggester import generate_insights
#                     result = generate_insights(merged_df, selected_title, "groq")
#                     compare_session["insights"].append({"question": selected_title, "result": result})
#                     st.success("Insight Generated")
#                     st.markdown(result)
#                 except Exception as e:
#                     st.error(f"Insight generation failed: {str(e)}")
#         else:
#             st.warning("No comparison insights available.")

#         st.subheader("💬 Chat About This Comparison")
#         compare_prompt = st.chat_input("Ask a question about the comparison...", key="chat_input_compare")
#         if compare_prompt:
#             result = handle_user_query_dynamic(compare_prompt, merged_df)
#             compare_session["chat_history"].append({"user": compare_prompt, "assistant": result})

#         for msg in compare_session["chat_history"][::-1]:
#             with st.chat_message("user"):
#                 st.markdown(msg["user"])
#             with st.chat_message("assistant"):
#                 st.markdown(msg["assistant"].get("response", msg["assistant"]))

#     else:
#         st.info("Please upload datasets to compare.")

import streamlit as st
from io import BytesIO
from utils.file_loader import load_data, clean_data
from utils.column_selector import get_important_columns
from utils.visualizer import visualize_from_llm_response
from utils.chat_handler import handle_user_query_dynamic
from utils.pdf_exporter import generate_pdf_report, export_to_pptx
from utils.insight_suggester import generate_insights, generate_insight_suggestions
from utils.llm_selector import get_llm
from utils.error_handler import safe_llm_call
import pandas as pd
import json
import re
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="Dynamic Impact Tool", layout="wide")
st.title("📊 Dynamic Dataset Analyzer")
# ==================== SESSION INITIALIZATION ==================== #
if "dataset_sessions" not in st.session_state:
    st.session_state["dataset_sessions"] = {}
if "current_session" not in st.session_state:
    st.session_state["current_session"] = None
if "compare_sessions" not in st.session_state:
    st.session_state["compare_sessions"] = {}
if "current_compare" not in st.session_state:
    st.session_state["current_compare"] = None

# ==================== SIDEBAR ==================== #
with st.sidebar:
    st.title("Dynamic Impact Tool")
    model_source = st.selectbox("Model", ["groq", "ollama"], key="sidebar_model")

    st.markdown("## 📥 Upload Dataset")
    uploaded_file = st.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"], key="sidebar_upload")
    file_path = st.text_input("Or Enter File Path")

    if st.button("Upload Dataset"):
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
                    "visualization_history": [],
                    "column_selection": []
                }

            st.session_state["current_session"] = file_name
            st.toast(f"✅ {file_name} uploaded successfully.")
            st.rerun()

        elif file_path:
            try:
                file_name = file_path.split("/")[-1]
                file = open(file_path, "rb")
                df, _ = load_data(file, file_name)
                df = clean_data(df)

                if file_name not in st.session_state["dataset_sessions"]:
                    st.session_state["dataset_sessions"][file_name] = {
                        "df": df,
                        "chat_history": [],
                        "insight_categories": [],
                        "selected_insight_results": [],
                        "visualization_history": [],
                        "column_selection": [],
                        "compare_sessions": {},              
                        "compare_history": [],               
                        "current_compare": None              
                    }

                st.session_state["current_session"] = file_name
                st.toast(f"✅ {file_name} uploaded successfully.")
                st.rerun()

            except Exception as e:
                st.error(f"File not found: {e}")
        else:
            st.warning("Please upload a file or enter a valid path.")

    st.markdown("## 🗂️ Dataset History")
    dataset_names = list(st.session_state["dataset_sessions"].keys())

    if dataset_names:
        selected_dataset = st.radio("Select Dataset Session", dataset_names,
                                    index=dataset_names.index(st.session_state["current_session"]) if st.session_state["current_session"] else 0)

        if selected_dataset != st.session_state["current_session"]:
            st.session_state["current_session"] = selected_dataset
            st.toast(f"✅ Switched to {selected_dataset}")
            st.rerun()

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
        st.experimental_rerun()

# ==================== MAIN TABS ==================== #
tab1, tab2, tab3 = st.tabs(["📊 Upload & Visualize", "🧠 Insights", "🔁 Compare Datasets"])

# ==================== TAB 1: Upload & Visualize ==================== #

with tab1:
    st.header("📊 Upload & Visualize")

    if st.session_state["current_session"]:
        session = st.session_state["dataset_sessions"][st.session_state["current_session"]]
        df = session["df"]
        st.subheader("📋 Dataset Summary")
        st.write(f"Total Rows: {df.shape[0]}")
        st.write(f"Total Columns: {df.shape[1]}")

        st.subheader("👁 Dataset Preview")
        sample_rows = st.slider("Preview Rows Limit", 0, 100, 10, key="sample_rows_visualize")
        st.dataframe(df.head(sample_rows), use_container_width=True)

        st.subheader("🗂 Column Selection")
        important_cols = get_important_columns(df.to_csv(index=False))
        user_selected_cols = st.multiselect("Select Additional Columns", df.columns.tolist(), default=important_cols)

        final_cols = list(set(important_cols + user_selected_cols))
        session["column_selection"] = final_cols

        st.write(f"Selected Columns: {final_cols}")
        st.dataframe(df[final_cols].head(), use_container_width=True)

        st.subheader("📈 Visualizations")
        x_axis = st.selectbox("Select X-Axis", final_cols)
        y_axis = st.selectbox("Select Y-Axis", final_cols)
        chart_type = st.selectbox("Chart Type", ["bar", "line", "scatter", "box", "violin", "area", "pie"])

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

        # st.markdown("## 💬 Ask Your Data")

        user_prompt_1 = st.chat_input("💬 Ask a question about your dataset...", key = "chat_input_visualize")
        if user_prompt_1:
           
           with st.spinner("Thinking..."):
              result = safe_llm_call(handle_user_query_dynamic, user_prompt_1, df, model_source, default={"response": "No response."})
           session["chat_history"].append({"user": user_prompt_1, "assistant": result})

        for msg in session["chat_history"][::-1]:
           with st.chat_message("user"):
            st.markdown(msg["user"])
           with st.chat_message("assistant"):
            st.markdown(msg["assistant"].get("response", msg["assistant"]))


        

# ==================== TAB 2: Insights ==================== #
with tab2:
    st.header("🧠 Insights")

    if st.session_state["current_session"]:
        session = st.session_state["dataset_sessions"][st.session_state["current_session"]]
        df = session["df"]

        # Main layout: Insights on the left, Categories on the right
        left_col, right_col = st.columns([7, 3], gap="large")

        # ==================== Left: Generated Insights ==================== #
        with left_col:
            st.subheader("📋 Generated Insights")
            if session["selected_insight_results"]:
                for insight in session["selected_insight_results"][::-1]:
                    with st.container(border=True):
                        st.markdown(f"**🔍 {insight['question']}**")
                        st.markdown(insight["result"])
                        st.markdown("---")
            else:
                st.info("No insights generated yet. Please select a question from the right.")

        # ==================== Right: Insight Categories ==================== #
        with right_col:
            st.subheader("🔍 Insight Categories")

            if not session["insight_categories"]:
                try:
                    preview = df.head(10).to_csv(index=False)[:2048]
                    llm = get_llm(model_source)

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

            if session["insight_categories"]:
                for idx, category in enumerate(session["insight_categories"]):
                    with st.expander(f"📂 {category['title']}"):
                        for question in category["questions"]:
                            if st.button(f"🔎 {question}", key=f"insight_{idx}_{question}"):
                                try:
                                    with st.spinner("Generating insight..."):
                                        result = generate_insights(df, question, model_source)
                                        session["selected_insight_results"].append({"question": question, "result": result})
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Insight generation failed: {e}")
            else:
                st.info("No categories available. Please upload a dataset first.")

        # ==================== Bottom: Chatbot ==================== #
        st.markdown("---")
        st.subheader("💬 Ask Your Data")

        user_prompt = st.chat_input("💬 Ask a question about your dataset...", key="chat_input_insights")
        if user_prompt:
            with st.spinner("Thinking..."):
                result = safe_llm_call(handle_user_query_dynamic, user_prompt, df, model_source, default={"response": "No response."})
            session["chat_history"].append({"user": user_prompt, "assistant": result})

        for msg in session["chat_history"][::-1]:
            with st.chat_message("user"):
                st.markdown(msg["user"])
            with st.chat_message("assistant"):
                st.markdown(msg["assistant"].get("response", msg["assistant"]))

# ==================== TAB 3: Compare Datasets ==================== #

# with tab3:
#     st.header("🔁 Compare Datasets")

#     st.subheader("📤 Upload Files for Comparison")
#     col1, col2 = st.columns(2)

#     uploaded_file1 = col1.file_uploader("Upload Dataset 1", type=["csv", "xlsx", "json"], key="compare_upload_1")
#     uploaded_file2 = col2.file_uploader("Upload Dataset 2", type=["csv", "xlsx", "json"], key="compare_upload_2")

#     file_path1 = col1.text_input("Or Enter Path for Dataset 1")
#     file_path2 = col2.text_input("Or Enter Path for Dataset 2")

#     if "compare_sessions" not in session:
#         st.session_state["compare_sessions"] = {}

#     if "compare_history" not in session:
#         st.session_state["compare_history"] = []

#     if st.button("Upload and Compare"):
#         try:
#             if uploaded_file1 is not None and uploaded_file2 is not None:
#                 file_name1 = uploaded_file1.name
#                 file_name2 = uploaded_file2.name
#                 df1, _ = load_data(BytesIO(uploaded_file1.read()), file_name1)
#                 df2, _ = load_data(BytesIO(uploaded_file2.read()), file_name2)

#             elif file_path1 and file_path2:
#                 file_name1 = file_path1.split("/")[-1]
#                 file_name2 = file_path2.split("/")[-1]
#                 df1, _ = load_data(open(file_path1, "rb"), file_name1)
#                 df2, _ = load_data(open(file_path2, "rb"), file_name2)

#             else:
#                 st.warning("Please upload both datasets or provide file paths.")
#                 st.stop()

#             df1 = clean_data(df1)
#             df2 = clean_data(df2)

#             compare_key = f"{file_name1} vs {file_name2}"
#             st.session_state["compare_sessions"][compare_key] = {
#                 "df1": df1,
#                 "df2": df2,
#                 "chat_history": [],
#                 "insights": [],
#                 "visualization_history": []
#             }
#             st.session_state["current_compare"] = compare_key
#             st.session_state["compare_history"].append(compare_key)
#             st.toast(f"✅ Comparison loaded: {compare_key}")
#             st.rerun()

#         except Exception as e:
#             st.error(f"Comparison upload failed: {e}")

#     if "current_compare" in st.session_state:
#         compare_key = st.session_state["current_compare"]
#         compare_session = st.session_state["compare_sessions"][compare_key]

#         df1 = compare_session["df1"]
#         df2 = compare_session["df2"]

#         st.success(f"Currently Comparing: {compare_key}")

#         st.subheader("📋 Dataset Previews")
#         col1, col2 = st.columns(2)
#         with col1:
#             st.markdown("#### Dataset 1")
#             st.dataframe(df1.head(), use_container_width=True)
#         with col2:
#             st.markdown("#### Dataset 2")
#             st.dataframe(df2.head(), use_container_width=True)

#         st.subheader("🗂 Column Selection for Comparison")
#         common_cols = list(set(df1.columns).intersection(set(df2.columns)))
#         if not common_cols:
#             st.warning("No common columns found between both datasets.")
#             st.stop()

#         x_axis = st.selectbox("Select X-Axis for Comparison", common_cols, key="compare_x_axis")
#         y_axis = st.selectbox("Select Y-Axis for Comparison", common_cols, key="compare_y_axis")
#         chart_type = st.selectbox("Chart Type", ["bar", "line", "scatter"], key="compare_chart")
#         layout = st.radio("Layout", ["Overlay", "Side-by-Side"], horizontal=True, key="compare_layout")

#         if x_axis and y_axis:
#             from utils.visualizer import visualize_comparison_overlay, visualize_comparison_side_by_side
#             try:
#                 if layout == "Overlay":
#                     fig, explanation = visualize_comparison_overlay(df1, df2, x_axis, y_axis, "Dataset 1", "Dataset 2", chart_type)
#                     st.plotly_chart(fig, use_container_width=True)
#                     st.caption(explanation)
#                     compare_session["visualization_history"].append(f"{chart_type} chart: {x_axis} vs {y_axis} (Overlay)")
#                 else:
#                     fig1, fig2 = visualize_comparison_side_by_side(df1, df2, x_axis, y_axis, chart_type)
#                     col1, col2 = st.columns(2)
#                     col1.plotly_chart(fig1, use_container_width=True)
#                     col2.plotly_chart(fig2, use_container_width=True)
#                     compare_session["visualization_history"].append(f"{chart_type} chart: {x_axis} vs {y_axis} (Side-by-Side)")

#             except Exception as e:
#                 st.error(f"Comparison visualization failed: {e}")

#         st.subheader("🧠 Suggested Comparison Insights")
#         merged_df = pd.concat([df1.assign(dataset="Dataset 1"), df2.assign(dataset="Dataset 2")])
#         preview = merged_df.head(10).to_csv(index=False)[:2048]

#         if "compare_insight_suggestions" not in compare_session:
#             from utils.insight_suggester import generate_insight_suggestions
#             try:
#                 suggestions = generate_insight_suggestions(preview, "groq")
#                 compare_session["compare_insight_suggestions"] = suggestions
#             except Exception as e:
#                 st.warning(f"Insight suggestion failed: {e}")
#                 compare_session["compare_insight_suggestions"] = []

#         titles = [s["title"] for s in compare_session.get("compare_insight_suggestions", [])]
#         if titles:
#             selected_title = st.selectbox("Select Comparison Insight", titles, key="selected_comparison_dropdown")
#             if st.button("Generate Comparison Insight", key="generate_comparison_insight"):
#                 try:
#                     from utils.insight_suggester import generate_insights
#                     result = generate_insights(merged_df, selected_title, "groq")
#                     compare_session["insights"].append({"question": selected_title, "result": result})
#                     st.success("Insight Generated")
#                     st.markdown(result)
#                 except Exception as e:
#                     st.error(f"Insight generation failed: {str(e)}")
#         else:
#             st.warning("No comparison insights available.")

#         st.subheader("💬 Chat About This Comparison")
#         compare_prompt = st.chat_input("Ask a question about the comparison...", key="chat_input_compare")
#         if compare_prompt:
#             result = handle_user_query_dynamic(compare_prompt, merged_df)
#             compare_session["chat_history"].append({"user": compare_prompt, "assistant": result})

#         for msg in compare_session["chat_history"][::-1]:
#             with st.chat_message("user"):
#                 st.markdown(msg["user"])
#             with st.chat_message("assistant"):
#                 st.markdown(msg["assistant"].get("response", msg["assistant"]))

#     else:
#         st.info("Please upload datasets to compare.")

with tab3:
    st.header("🔁 Compare Datasets")

    # Get the current dataset session
    if st.session_state["current_session"]:
        session = st.session_state["dataset_sessions"][st.session_state["current_session"]]
    else:
        st.warning("Please upload or select a dataset session first.")
        st.stop()

    st.subheader("📤 Upload Files for Comparison")
    col1, col2 = st.columns(2)

    uploaded_file1 = col1.file_uploader("Upload Dataset 1", type=["csv", "xlsx", "json"], key="compare_upload_1")
    uploaded_file2 = col2.file_uploader("Upload Dataset 2", type=["csv", "xlsx", "json"], key="compare_upload_2")

    file_path1 = col1.text_input("Or Enter Path for Dataset 1")
    file_path2 = col2.text_input("Or Enter Path for Dataset 2")

    # Initialize comparison storage inside the current dataset session
    if "compare_sessions" not in session:
        session["compare_sessions"] = {}
    if "compare_history" not in session:
        session["compare_history"] = []
    if "current_compare" not in session:
        session["current_compare"] = None

    if st.button("Upload and Compare"):
        try:
            if uploaded_file1 is not None and uploaded_file2 is not None:
                file_name1 = uploaded_file1.name
                file_name2 = uploaded_file2.name
                df1, _ = load_data(BytesIO(uploaded_file1.read()), file_name1)
                df2, _ = load_data(BytesIO(uploaded_file2.read()), file_name2)

            elif file_path1 and file_path2:
                file_name1 = file_path1.split("/")[-1]
                file_name2 = file_path2.split("/")[-1]
                df1, _ = load_data(open(file_path1, "rb"), file_name1)
                df2, _ = load_data(open(file_path2, "rb"), file_name2)

            else:
                st.warning("Please upload both datasets or provide file paths.")
                st.stop()

            df1 = clean_data(df1)
            df2 = clean_data(df2)

            compare_key = f"{file_name1} vs {file_name2}"
            session["compare_sessions"][compare_key] = {
                "df1": df1,
                "df2": df2,
                "chat_history": [],
                "insights": [],
                "visualization_history": []
            }
            session["current_compare"] = compare_key
            session["compare_history"].append(compare_key)
            st.toast(f"✅ Comparison loaded: {compare_key}")
            st.rerun()

        except Exception as e:
            st.error(f"Comparison upload failed: {e}")

    if session["current_compare"]:
        compare_key = session["current_compare"]
        compare_session = session["compare_sessions"][compare_key]

        df1 = compare_session["df1"]
        df2 = compare_session["df2"]

        st.success(f"Currently Comparing: {compare_key}")

        st.subheader("📋 Dataset Previews")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Dataset 1")
            st.dataframe(df1.head(), use_container_width=True)
        with col2:
            st.markdown("#### Dataset 2")
            st.dataframe(df2.head(), use_container_width=True)

        st.subheader("🗂 Column Selection for Comparison")
        common_cols = list(set(df1.columns).intersection(set(df2.columns)))
        if not common_cols:
            st.warning("No common columns found between both datasets.")
            st.stop()

        x_axis = st.selectbox("Select X-Axis for Comparison", common_cols, key="compare_x_axis")
        y_axis = st.selectbox("Select Y-Axis for Comparison", common_cols, key="compare_y_axis")
        chart_type = st.selectbox("Chart Type", ["bar", "line", "scatter"], key="compare_chart")
        layout = st.radio("Layout", ["Overlay", "Side-by-Side"], horizontal=True, key="compare_layout")

        if x_axis and y_axis:
            from utils.visualizer import visualize_comparison_overlay, visualize_comparison_side_by_side
            try:
                if layout == "Overlay":
                    fig, explanation = visualize_comparison_overlay(df1, df2, x_axis, y_axis, "Dataset 1", "Dataset 2", chart_type)
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption(explanation)
                    compare_session["visualization_history"].append(f"{chart_type} chart: {x_axis} vs {y_axis} (Overlay)")
                else:
                    fig1, fig2 = visualize_comparison_side_by_side(df1, df2, x_axis, y_axis, chart_type)
                    col1, col2 = st.columns(2)
                    col1.plotly_chart(fig1, use_container_width=True)
                    col2.plotly_chart(fig2, use_container_width=True)
                    compare_session["visualization_history"].append(f"{chart_type} chart: {x_axis} vs {y_axis} (Side-by-Side)")

            except Exception as e:
                st.error(f"Comparison visualization failed: {e}")

        st.subheader("🧠 Suggested Comparison Insights")
        merged_df = pd.concat([df1.assign(dataset="Dataset 1"), df2.assign(dataset="Dataset 2")])
        preview = merged_df.head(10).to_csv(index=False)[:2048]

        if "compare_insight_suggestions" not in compare_session:
            from utils.insight_suggester import generate_insight_suggestions
            try:
                suggestions = generate_insight_suggestions(preview, "groq")
                compare_session["compare_insight_suggestions"] = suggestions
            except Exception as e:
                st.warning(f"Insight suggestion failed: {e}")
                compare_session["compare_insight_suggestions"] = []

        titles = [s["title"] for s in compare_session.get("compare_insight_suggestions", [])]
        if titles:
            selected_title = st.selectbox("Select Comparison Insight", titles, key="selected_comparison_dropdown")
            if st.button("Generate Comparison Insight", key="generate_comparison_insight"):
                try:
                    from utils.insight_suggester import generate_insights
                    result = generate_insights(merged_df, selected_title, "groq")
                    compare_session["insights"].append({"question": selected_title, "result": result})
                    st.success("Insight Generated")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Insight generation failed: {str(e)}")
        else:
            st.warning("No comparison insights available.")

        st.subheader("💬 Chat About This Comparison")
        compare_prompt = st.chat_input("Ask a question about the comparison...", key="chat_input_compare")
        if compare_prompt:
            result = handle_user_query_dynamic(compare_prompt, merged_df)
            compare_session["chat_history"].append({"user": compare_prompt, "assistant": result})

        for msg in compare_session["chat_history"][::-1]:
            with st.chat_message("user"):
                st.markdown(msg["user"])
            with st.chat_message("assistant"):
                st.markdown(msg["assistant"].get("response", msg["assistant"]))

    else:
        st.info("Please upload datasets to compare.")
