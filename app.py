# import os
# import streamlit as st
# from dotenv import load_dotenv
# import pandas as pd
# from utils.file_loader import load_data,clean_data
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
# import sys
# import os
# sys.path.append(os.path.abspath('./config'))
# from utils.column_selector import get_important_columns
# from utils.llm_selector import get_llm

# load_dotenv()
# st.set_page_config(page_title="Dynamic Impact Tool", layout="wide")

# for key in ["df", "df1", "df2", "insights", "chat_history", "compare_chat"]:
#     if key not in st.session_state:
#         st.session_state[key] = [] if "chat" in key else None

# with st.sidebar:
#     st.title("Dynamic Impact Tool")
#     section = st.radio("Navigate", ["Upload & Visualize","Insights", "Compare Datasets", "Summary & Export"], key="sidebar_section")
#     model_source = st.selectbox("Model", ["groq", "ollama"], key="sidebar_model")


# # === Section 1: Upload & Insights ===
# if section == "Upload & Visualize":
#     st.header("📥 Upload Dataset")

#     # === Upload CSV/Excel/JSON or Provide Path ===
#     col1, col2 = st.columns(2)
#     uploaded_file = col1.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"], key="upload_main")
#     file_path = col2.text_input("Or Enter File Path", key="path_main")

#     # === Clean path and try loading file ===
#     cleaned_path = file_path.strip() if file_path else None
#     try:
#         file = open(cleaned_path, "rb") if cleaned_path else uploaded_file
#     except FileNotFoundError:
#         st.error(f"❌ File not found: {cleaned_path}")
#         file = None

#     # === Sample Preview Slider ===
#     sample_rows = st.slider("Preview Rows Limit (for display only)", 0, 100, 10, key="sample_rows_upload")

#     if file:
#         df, _ = load_data(file)  # load full dataset always
#         df = clean_data(df)
#         st.session_state.df = df
#         st.success(f"✅ Dataset Loaded with {len(df)} rows and {len(df.columns)} columns")

#         st.markdown("### 👁️ Preview")
#         if sample_rows > 0:
#             st.dataframe(df.head(sample_rows), use_container_width=True)
#         else:
#             st.dataframe(df, use_container_width=True)

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
#                 llm_response = {
#                     "chart_type": chart_type,
#                     "x": x_axis,
#                     "y": y_axis,
#                     "group_by": None
#                 }
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

#         if "insight_suggestions" not in st.session_state:
#             try:
#                 suggestions = generate_insight_suggestions(preview, model_source)
#                 st.session_state.insight_suggestions = suggestions
#             except Exception as e:
#                 st.session_state.insight_suggestions = []
#                 st.warning(f"Insight suggestion failed: {e}")

#         titles = [s["title"] for s in st.session_state.insight_suggestions]
#         if titles:
#             selected_title = st.selectbox("Select Insight to Generate", titles, key="insight_dropdown")
#             if st.button("Generate Insight"):
#                 try:
#                     insight_result = generate_insights(df, selected_title, model_source)
#                     st.session_state.insights = {"response": insight_result}
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
#             result = safe_llm_call(handle_user_query_dynamic, user_prompt, df, model_source, default={"response": "No response."})
#             st.session_state.chat_history.append({"user": user_prompt, "assistant": result})

#         for msg in st.session_state.chat_history[::-1]:
#             with st.chat_message("user"):
#                 st.markdown(msg["user"])
#             with st.chat_message("assistant"):
#                 st.markdown(msg["assistant"].get("response", msg["assistant"]))


# # === Section 2: Insights ===
# if section == "Insights":
#     st.header("🧠 Insight Discovery Center")

#     col1, col2, col3 = st.columns([0.1, 0.7, 0.2])  # Left spacing, Center content, Right sidebar

#     # --- Center: Insight Display ---
#     with col2:
#         st.subheader("📋 Insight Result")
#         if "selected_insight_result" in st.session_state:
#             st.markdown(st.session_state["selected_insight_result"])
#         else:
#             st.info("Select an insight question from the right to see results here.")

#     # --- Right: Insight Sidebar ---
#     with col3:
#         st.subheader("🔍 Insight Categories")

#         # Check if dataset is loaded
#         if "df" in st.session_state and st.session_state.df is not None:
#             df = st.session_state.df

#             # Generate categories if not already available
#             if "insight_categories" not in st.session_state:
#                 try:
#                     preview = df.head(10).to_csv(index=False)[:2048]
#                     categories = generate_insight_suggestions(preview, model_source)  # Should return categories
#                     st.session_state.insight_categories = categories
#                 except Exception as e:
#                     st.warning(f"Insight suggestion failed: {e}")
#                     st.session_state.insight_categories = []
            
#             categories = st.session_state.get("insight_categories", [])

#             if categories:
#                 for category in categories:
#                     with st.expander(f"📂 {category['title']}"):
#                         for question in category.get("questions", []):
#                             if st.button(question):
#                                 with st.spinner("Generating insight..."):
#                                     try:
#                                         result = generate_insights(df, question, model_source)
#                                         st.session_state["selected_insight_result"] = result
#                                         st.experimental_rerun()
#                                     except Exception as e:
#                                         st.error(f"Insight generation failed: {e}")
#             else:
#                 st.info("No categories available. Please upload a dataset in 'Upload & Insights' tab.")
#         else:
#             st.warning("No dataset loaded. Please upload a dataset first.")

#     # --- Chat Input at Bottom ---
#     st.markdown("---")
#     user_prompt = st.chat_input("💬 Ask a question about your dataset...")
#     if user_prompt:
#         result = safe_llm_call(handle_user_query_dynamic, user_prompt, st.session_state.df, model_source, default={"response": "No response."})
#         st.session_state.chat_history.append({"user": user_prompt, "assistant": result})

#     for msg in st.session_state.chat_history[::-1]:
#         with st.chat_message("user"):
#             st.markdown(msg["user"])
#         with st.chat_message("assistant"):
#             st.markdown(msg["assistant"].get("response", msg["assistant"]))


# # === Section 3: Compare Datasets ===
# if section == "Compare Datasets":
#     st.header("📊 Compare Datasets")

#     # === File Upload and Path Input ===
#     col1, col2 = st.columns(2)

#     uploaded_file1 = col1.file_uploader("Upload Dataset 1", type=["csv", "xlsx", "json"], key="upload_1")
#     file_path1 = col1.text_input("Or Enter Path for Dataset 1", key="path_1")

#     uploaded_file2 = col2.file_uploader("Upload Dataset 2", type=["csv", "xlsx", "json"], key="upload_2")
#     file_path2 = col2.text_input("Or Enter Path for Dataset 2", key="path_2")

#     # Clean file paths
#     cleaned_path1 = file_path1.strip() if file_path1 else None
#     cleaned_path2 = file_path2.strip() if file_path2 else None

#     file1, file2 = None, None
#     try:
#         file1 = open(cleaned_path1, "rb") if cleaned_path1 else uploaded_file1
#     except FileNotFoundError:
#         st.error(f"File not found: {cleaned_path1}")
#     try:
#         file2 = open(cleaned_path2, "rb") if cleaned_path2 else uploaded_file2
#     except FileNotFoundError:
#         st.error(f"File not found: {cleaned_path2}")

#     # === Data Loading ===
#     if file1 and file2:
#         try:
#             df1, _ = load_data(file1)
#             df2, _ = load_data(file2)
#             df1, df2 = clean_data(df1), clean_data(df2)

#             if not isinstance(df1, pd.DataFrame) or not isinstance(df2, pd.DataFrame):
#                 st.error("❌ One or both datasets could not be parsed as valid DataFrames.")
#                 st.stop()

#             df1.columns = [col.strip().lower() for col in df1.columns]
#             df2.columns = [col.strip().lower() for col in df2.columns]

#             st.session_state.df1 = df1
#             st.session_state.df2 = df2
#             st.success("✅ Both datasets loaded successfully.")

#             # === Dataset Preview ===
#             st.subheader("📋 Dataset Previews")
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.markdown("#### Dataset 1")
#                 st.dataframe(df1.head(), use_container_width=True)
#             with col2:
#                 st.markdown("#### Dataset 2")
#                 st.dataframe(df2.head(), use_container_width=True)

#             # === AI + USER COLUMN SELECTION ===
#             st.subheader("🧠 AI + User Column Selector")

#             ai_cols1 = get_important_columns(df1.to_csv(index=False), model_source)
#             ai_cols1 = [col.strip().lower() for col in ai_cols1]
#             matched_in_df2 = [col for col in ai_cols1 if col in df2.columns]
#             missing_in_df2 = list(set(ai_cols1) - set(matched_in_df2))
#             st.info(f"⚠️ Missing in Dataset 2: {', '.join(missing_in_df2) if missing_in_df2 else 'None'}")

#             col1, col2 = st.columns(2)
#             with col1:
#                 user_cols1 = st.multiselect("✅ Select Additional Columns from Dataset 1", df1.columns.tolist(), default=ai_cols1, key="manual_cols_1")
#                 final_cols1 = list(set(ai_cols1 + user_cols1))
#                 st.success(f"Selected Columns in Dataset 1: {final_cols1}")
#             with col2:
#                 final_cols2 = [col for col in final_cols1 if col in df2.columns]
#                 st.success(f"Matched Columns in Dataset 2: {final_cols2}")
#                 if not final_cols2:
#                     st.warning("🚫 No common columns between selected Dataset 1 columns and Dataset 2.")

#             df1 = df1[final_cols1] if final_cols1 else df1
#             df2 = df2[final_cols2] if final_cols2 else df2

#             # === Manual Comparison Visualization ===
#             st.subheader("📈 Manual Comparison Visualization")
#             common_cols = list(set(df1.columns).intersection(set(df2.columns)))

#             if not common_cols:
#                 st.warning("⚠️ No common columns to visualize.")
#             else:
#                 x_axis = st.selectbox("📌 Select X-Axis", common_cols, key="compare_x_axis")
#                 y_axis = st.selectbox("📌 Select Y-Axis", common_cols, key="compare_y_axis")
#                 layout = st.radio("🧩 Layout", ["Overlay", "Side-by-Side"], horizontal=True, key="compare_layout")
#                 chart_type = st.selectbox("📈 Chart Type", ["bar", "line", "scatter"], key="compare_chart")

#                 if layout == "Overlay":
#                     fig, explanation = visualize_comparison_overlay(df1, df2, x_axis, y_axis, "Dataset 1", "Dataset 2", chart_type)
#                     st.plotly_chart(fig, use_container_width=True)
#                     st.caption(explanation)
#                 else:
#                     fig1, fig2 = visualize_comparison_side_by_side(df1, df2, x_axis, y_axis, chart_type)
#                     col1, col2 = st.columns(2)
#                     col1.plotly_chart(fig1, use_container_width=True)
#                     col2.plotly_chart(fig2, use_container_width=True)

#             # === AI-Suggested Comparison Insight Titles ===
#             st.subheader("🧠 Suggested Comparison Insights")
#             merged_df = pd.concat([
#                 df1.assign(dataset="Dataset 1"),
#                 df2.assign(dataset="Dataset 2")
#             ])
#             preview = merged_df.head(10).to_csv(index=False)[:2048]

#             if "compare_insight_suggestions" not in st.session_state:
#                 try:
#                     titles = generate_insight_suggestions(preview, model_source)
#                     st.session_state.compare_insight_suggestions = titles
#                 except Exception as e:
#                     st.warning(f"Insight suggestion failed: {e}")
#                     st.session_state.compare_insight_suggestions = []

#             titles = [t["title"] for t in st.session_state.compare_insight_suggestions]
#             if titles:
#                 selected_compare_title = st.selectbox("🧠 Select Insight to Generate", titles, key="selected_comparison_dropdown")

#                 if st.button("Generate Comparison Insight", key="dynamic_comparison_insight"):
#                     try:
#                         insight_result = generate_insights(merged_df, selected_compare_title, model_source)
#                         st.success("Insight Generated")
#                         st.markdown(insight_result)
#                         st.session_state.insights = {"response": insight_result}
#                     except Exception as e:
#                         st.error(f"Insight generation failed: {str(e)}")
#             else:
#                 st.warning("No insights available to suggest.")

#             # === Chat with Comparison Datasets ===
#             st.subheader("💬 Chat About This Comparison")
#             compare_prompt = st.chat_input("Ask a question about the comparison...")
#             if compare_prompt:
#                 result = safe_llm_call(handle_user_query_dynamic, compare_prompt, merged_df, model_source, default={"response": "No response."})
#                 st.session_state.compare_chat.append({"user": compare_prompt, "assistant": result})

#             for msg in st.session_state.compare_chat[::-1]:
#                 with st.chat_message("user"):
#                     st.markdown(msg["user"])
#                 with st.chat_message("assistant"):
#                     st.markdown(msg["assistant"].get("response", msg["assistant"]))

#         except Exception as e:
#             st.error(f"❌ Failed to load or compare datasets: {e}")
#     else:
#         st.warning("⚠️ Please upload or enter a valid path for both datasets.")



# # === Section 3: Summary & Export ===
# if section == "Summary & Export":
#     st.header("📦 Summary & Export")

#     insights = st.session_state.get("insights", "No insights generated yet.")
#     chat_logs = st.session_state.get("chat_history", []) + st.session_state.get("compare_chat", [])

#     # --- Insight Summary ---
#     st.subheader("Insight Summary")
#     if insights:
#         st.markdown(insights)
#     else:
#         st.warning("No insights to display.")

#     # --- Chat History ---
#     if chat_logs:
#         st.subheader("Chat History")
#         for msg in chat_logs[::-1]:
#             with st.chat_message("user"):
#                 st.markdown(msg["user"])
#             with st.chat_message("assistant"):
#                 st.markdown(msg["assistant"].get("response", msg["assistant"]))
#     insights_summary = ""
#     if st.session_state.insights:
#         if isinstance(st.session_state.insights, dict) and "response" in st.session_state.insights:
#             insights_summary = st.session_state.insights["response"]
#         else:
#             insights_summary = str(st.session_state.insights)

#     all_chat_logs = st.session_state.chat_history + st.session_state.compare_chat

#     # --- Export Buttons ---
#     st.subheader("📁 Export Report")
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("📄 Export PDF"):
#             try:
#                 pdf_path = generate_pdf_report(insights_summary, all_chat_logs)
#                 with open(pdf_path, "rb") as f:
#                     st.download_button("Download PDF", f, file_name="summary.pdf")
#             except Exception as e:
#                 st.error(f"Failed to export PDF: {e}")

#     with col2:
#         if st.button("📊 Export PPTX"):
#             try:
#                 pptx_path = export_to_pptx(insights_summary, all_chat_logs)
#                 with open(pptx_path, "rb") as f:
#                     st.download_button("Download PPTX", f, file_name="summary.pptx")
#             except Exception as e:
#                 st.error(f"Failed to export PPTX: {e}")

# Dynamic Impact Tool - Cleaned and Updated App

import os
import json
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
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
for key in ["df", "df1", "df2", "insights", "chat_history", "compare_chat", "insight_categories"]:
    if key not in st.session_state:
        st.session_state[key] = [] if "chat" in key else None

# Sidebar Navigation
with st.sidebar:
    st.title("Dynamic Impact Tool")
    section = st.radio("Navigate", ["Upload & Insights", "Compare Datasets", "Insights", "Summary & Export"], key="sidebar_section")
    model_source = st.selectbox("Model", ["groq", "ollama"], key="sidebar_model")

    st.markdown("---")
    if st.button("💾 Save Session"):
        with open("saved_session.json", "w") as f:
            json.dump(st.session_state._state.to_dict(), f)
        st.toast("✅ Session saved successfully.")

    if st.button("📂 Load Session"):
        try:
            with open("saved_session.json", "r") as f:
                saved_state = json.load(f)
            for key, value in saved_state.items():
                st.session_state[key] = value
            st.toast("✅ Session loaded successfully.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Failed to load session: {e}")

    if st.button("🧹 Clear Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# Upload & Insights Tab
if section == "Upload & Insights":
    st.header("📥 Upload Dataset")

    col1, col2 = st.columns(2)
    uploaded_file = col1.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"], key="upload_main")
    file_path = col2.text_input("Or Enter File Path", key="path_main")

    if "df" not in st.session_state or st.session_state.df is None:
        if uploaded_file is not None:
            with st.spinner("Loading uploaded file..."):
                df, _ = load_data(uploaded_file)
                df = clean_data(df)
                st.session_state.df = df
                st.toast("✅ Dataset loaded successfully.")
        elif file_path:
            try:
                with st.spinner("Loading file from path..."):
                    file = open(file_path.strip(), "rb")
                    df, _ = load_data(file)
                    df = clean_data(df)
                    st.session_state.df = df
                    st.toast("✅ Dataset loaded successfully.")
            except Exception as e:
                st.error(f"❌ File not found: {e}")
    else:
        df = st.session_state.df
        st.info("✅ Dataset already loaded.")

    if "df" in st.session_state and st.session_state.df is not None:
        df = st.session_state.df
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



if section == "Compare Datasets":
    st.header("📊 Compare Datasets")

    # === File Upload and Path Input ===
    col1, col2 = st.columns(2)

    uploaded_file1 = col1.file_uploader("Upload Dataset 1", type=["csv", "xlsx", "json"], key="upload_1")
    file_path1 = col1.text_input("Or Enter Path for Dataset 1", key="path_1")

    uploaded_file2 = col2.file_uploader("Upload Dataset 2", type=["csv", "xlsx", "json"], key="upload_2")
    file_path2 = col2.text_input("Or Enter Path for Dataset 2", key="path_2")

    # Clean file paths
    cleaned_path1 = file_path1.strip() if file_path1 else None
    cleaned_path2 = file_path2.strip() if file_path2 else None

    file1, file2 = None, None
    try:
        file1 = open(cleaned_path1, "rb") if cleaned_path1 else uploaded_file1
    except FileNotFoundError:
        st.error(f"File not found: {cleaned_path1}")
    try:
        file2 = open(cleaned_path2, "rb") if cleaned_path2 else uploaded_file2
    except FileNotFoundError:
        st.error(f"File not found: {cleaned_path2}")

    # === Data Loading ===
    if file1 and file2:
        try:
            df1, _ = load_data(file1)
            df2, _ = load_data(file2)
            df1, df2 = clean_data(df1), clean_data(df2)

            if not isinstance(df1, pd.DataFrame) or not isinstance(df2, pd.DataFrame):
                st.error("❌ One or both datasets could not be parsed as valid DataFrames.")
                st.stop()

            df1.columns = [col.strip().lower() for col in df1.columns]
            df2.columns = [col.strip().lower() for col in df2.columns]

            st.session_state.df1 = df1
            st.session_state.df2 = df2
            st.success("✅ Both datasets loaded successfully.")

            # === Dataset Preview ===
            st.subheader("📋 Dataset Previews")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Dataset 1")
                st.dataframe(df1.head(), use_container_width=True)
            with col2:
                st.markdown("#### Dataset 2")
                st.dataframe(df2.head(), use_container_width=True)

            # === AI + USER COLUMN SELECTION ===
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

            # === Manual Comparison Visualization ===
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

            # === AI-Suggested Comparison Insight Titles ===
            st.subheader("🧠 Suggested Comparison Insights")
            merged_df = pd.concat([
                df1.assign(dataset="Dataset 1"),
                df2.assign(dataset="Dataset 2")
            ])
            preview = merged_df.head(10).to_csv(index=False)[:2048]

            if "compare_insight_suggestions" not in st.session_state:
                try:
                    titles = generate_insight_suggestions(preview, model_source)
                    st.session_state.compare_insight_suggestions = titles
                except Exception as e:
                    st.warning(f"Insight suggestion failed: {e}")
                    st.session_state.compare_insight_suggestions = []

            titles = [t["title"] for t in st.session_state.compare_insight_suggestions]
            if titles:
                selected_compare_title = st.selectbox("🧠 Select Insight to Generate", titles, key="selected_comparison_dropdown")

                if st.button("Generate Comparison Insight", key="dynamic_comparison_insight"):
                    try:
                        insight_result = generate_insights(merged_df, selected_compare_title, model_source)
                        st.success("Insight Generated")
                        st.markdown(insight_result)
                        st.session_state.insights = {"response": insight_result}
                    except Exception as e:
                        st.error(f"Insight generation failed: {str(e)}")
            else:
                st.warning("No insights available to suggest.")

            # === Chat with Comparison Datasets ===
            st.subheader("💬 Chat About This Comparison")
            compare_prompt = st.chat_input("Ask a question about the comparison...")
            if compare_prompt:
                result = safe_llm_call(handle_user_query_dynamic, compare_prompt, merged_df, model_source, default={"response": "No response."})
                st.session_state.compare_chat.append({"user": compare_prompt, "assistant": result})

            for msg in st.session_state.compare_chat[::-1]:
                with st.chat_message("user"):
                    st.markdown(msg["user"])
                with st.chat_message("assistant"):
                    st.markdown(msg["assistant"].get("response", msg["assistant"]))

        except Exception as e:
            st.error(f"❌ Failed to load or compare datasets: {e}")
    else:
        st.warning("⚠️ Please upload or enter a valid path for both datasets.")




# Insights Tab
if section == "Insights":
    st.header("🧠 Insight Discovery Center")

    col1, col2, col3 = st.columns([0.1, 0.7, 0.2])

    with col2:
        st.subheader("📋 Insight Result")
        if "selected_insight_result" in st.session_state:
            st.markdown(st.session_state["selected_insight_result"])
        else:
            st.info("Select an insight question from the right to see results here.")

    with col3:
        st.subheader("🔍 Insight Categories")

        if "df" in st.session_state and st.session_state.df is not None:
            df = st.session_state.df

            if not st.session_state.insight_categories:
                try:
                    preview = df.head(10).to_csv(index=False)[:2048]
                    categories = generate_insight_suggestions(preview, model_source)
                    st.session_state.insight_categories = categories
                except Exception as e:
                    st.warning(f"Insight suggestion failed: {e}")
                    st.session_state.insight_categories = []

            categories = st.session_state.get("insight_categories", [])

            if categories:
                for category in categories:
                    with st.expander(f"📂 {category['title']}"):
                        for question in category.get("questions", []):
                            if st.button(question):
                                with st.spinner("Generating insight..."):
                                    try:
                                        result = generate_insights(df, question, model_source)
                                        st.session_state["selected_insight_result"] = result
                                        st.experimental_rerun()
                                    except Exception as e:
                                        st.error(f"Insight generation failed: {e}")
            else:
                st.info("No categories available. Please upload a dataset in 'Upload & Insights' tab.")
        else:
            st.warning("No dataset loaded. Please upload a dataset first.")

    st.markdown("---")
    user_prompt = st.chat_input("💬 Ask a question about your dataset...")
    if user_prompt:
        with st.spinner("Thinking..."):
            result = safe_llm_call(handle_user_query_dynamic, user_prompt, st.session_state.df, model_source, default={"response": "No response."})
        st.session_state.chat_history.append({"user": user_prompt, "assistant": result})

    for msg in st.session_state.chat_history[::-1]:
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant"):
            st.markdown(msg["assistant"].get("response", msg["assistant"]))
