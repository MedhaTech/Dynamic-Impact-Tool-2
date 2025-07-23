import streamlit as st
from io import BytesIO
import os
from utils.file_loader import load_data, clean_data
from utils.visualizer import visualize_comparison_overlay, visualize_comparison_side_by_side
from utils.visualizer import visualize_from_llm_response
from utils.insight_suggester import generate_insights
from utils.chat_handler import handle_user_query_dynamic
from utils.error_handler import safe_llm_call
import pandas as pd
from utils.column_selector import get_important_columns
from utils.insight_generator import generate_comparison_insight_suggestions
from utils.llm_selector import get_llm
from utils.pdf_exporter import generate_pdf_report, export_to_pptx
import re
import json
from utils.pdf_exporter_comparision import generate_pdf_report_comparison

import hashlib
import os
import re
from utils.visualizer import visualize_comparison_overlay  # or side_by_side if needed

def generate_comparison_plot_from_insight(df1, df2, question, result, dataset1_name="Dataset 1", dataset2_name="Dataset 2"):
    """
    Automatically generates and saves a comparison plot based on LLM-suggested insight.

    Parameters:
        df1 (pd.DataFrame): First dataset
        df2 (pd.DataFrame): Second dataset
        question (str): Insight question
        result (str): LLM response (may contain '[Insert graph here]')
        dataset1_name (str): Custom name of dataset 1
        dataset2_name (str): Custom name of dataset 2

    Returns:
        image_path (str): Path to saved image if generated, else None
    """

    if "[Insert graph here]" not in result:
        return None

    # Detect potential x and y axes from common columns
    common_cols = list(set(df1.columns).intersection(set(df2.columns)))
    if not common_cols:
        return None

    x_axis = common_cols[0]
    y_axis = common_cols[1] if len(common_cols) > 1 else common_cols[0]

    try:
        # Generate overlay plot (can also use side-by-side function)
        fig, explanation = visualize_comparison_overlay(df1, df2, x_axis, y_axis, dataset1_name, dataset2_name, chart_type="bar")

        # Save image
        os.makedirs("generated_plots", exist_ok=True)
        hash_name = hashlib.md5((question + x_axis + y_axis).encode()).hexdigest()
        image_path = f"generated_plots/{hash_name}.png"
        fig.write_image(image_path)

        return image_path

    except Exception as e:
        print(f"[Error in plot generation]: {e}")
        return None


def render_comparison_tabs():
    if "current_compare" not in st.session_state or st.session_state["current_compare"] is None:
        st.info("Please upload two datasets to compare.")
        return

    compare_key = st.session_state["current_compare"]
    compare_session = st.session_state["compare_sessions"][compare_key]

    df1 = compare_session["df1"]
    df2 = compare_session["df2"]

    st.success(f"Currently Comparing: {compare_key}")

    tab1, tab2, tab3 = st.tabs(["📋 Dataset Previews", "🧠 Comparison Insights", "Visualizations"])

    # ==================== Tab 1: Dataset Previews & Visualizations ==================== #
    with tab1:
        st.header("📋 Dataset Previews")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Dataset 1")
            st.dataframe(df1.head(), use_container_width=True)
        with col2:
            st.markdown("#### Dataset 2")
            st.dataframe(df2.head(), use_container_width=True)

        st.subheader("🧠 AI + User Column Selector")

        ai_cols1 = get_important_columns(df1.to_csv(index=False), "groq")
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

        compare_session["final_cols1"] = final_cols1
        compare_session["final_cols2"] = final_cols2

        
        common_cols = list(set(df1.columns).intersection(set(df2.columns)))

        if not common_cols:
            st.warning("No common columns found between both datasets.")
            st.stop()
      

    with tab3:
        st.header("📊 Comparison Visualizations")
        x_axis = st.selectbox("Select X-Axis for Comparison", common_cols, key="compare_x_axis")
        y_axis = st.selectbox("Select Y-Axis for Comparison", common_cols, key="compare_y_axis")
        chart_type = st.selectbox("Chart Type", ["bar", "line", "scatter"], key="compare_chart")
        layout = st.radio("Layout", ["Overlay", "Side-by-Side"], horizontal=True, key="compare_layout")

        if x_axis and y_axis:
            try:
                if layout == "Overlay":
                    fig, explanation = visualize_comparison_overlay(df1, df2, x_axis, y_axis, "Dataset 1", "Dataset 2", chart_type)
                    st.plotly_chart(fig, use_container_width=True)
                    compare_session["visualization_history"].append(f"{chart_type} chart: {x_axis} vs {y_axis} (Overlay)")
                    st.caption(explanation)
                else:
                    fig1, fig2 = visualize_comparison_side_by_side(df1, df2, x_axis, y_axis, chart_type)
                    col1, col2 = st.columns(2)
                    col1.plotly_chart(fig1, use_container_width=True)
                    col2.plotly_chart(fig2, use_container_width=True)
                    compare_session["visualization_history"].append(f"{chart_type} chart: {x_axis} vs {y_axis} (Side-by-Side)")
            except Exception as e:
                st.error(f"Comparison visualization failed: {e}")

    # ==================== Tab 2: Comparison Insights ==================== #






    with tab2:
     st.header("🧠 Comparison Insights")

     merged_df = pd.concat([df1.assign(dataset="Dataset 1"), df2.assign(dataset="Dataset 2")])

     col_left, col_right = st.columns([7, 3], gap="large")

     with col_left:
        st.markdown("### 📋 Generated Comparison Insights")
        if compare_session["insights"]:
            for insight in compare_session["insights"][::-1]:
                with st.container(border=True):
                    st.markdown(f"**🔍 {insight['question']}**")
                    st.markdown(insight["result"])
                    if any(term in insight["result"].lower() for term in ["graph", "visual", "chart", "plot"]):
                    # if "graph" in insight["result"].lower() or "visual" in insight["result"].lower() or "chart" in insight["result"].lower() or "plot" in insight["result"].lower():
                            try:
                                # Very basic detection of x/y axis from the answer text
                                x_axis, y_axis = None, None
                                for col in compare_session["final_cols1"]:
                                    if col.lower() in insight["result"].lower():
                                        if not x_axis:
                                            x_axis = col
                                        elif not y_axis and col != x_axis:
                                            y_axis = col

                                if x_axis and y_axis:
                                    fig1, fig2 = visualize_comparison_side_by_side(
                                         compare_session["df1"],
                                         compare_session["df2"],
                                         x_axis,
                                         y_axis,
                                         "bar"
                                    )
                                    col1, col2 = st.columns(2)
                                    col1.plotly_chart(fig1, use_container_width=True)
                                    col2.plotly_chart(fig2, use_container_width=True)
                                    import plotly.io as pio
                                    import hashlib
                                    os.makedirs("generated_plots", exist_ok=True)
                                    
                                    hash_name = hashlib.md5(insight["question"].encode()).hexdigest()
                                    image_path_1 = f"generated_plots/{hash_name}_1.png"
                                    pio.write_image(fig1, image_path_1)

                                    image_path_2 = f"generated_plots/{hash_name}_2.png"
                                    pio.write_image(fig2, image_path_2)

                                    # image_path_1 = f"generated_plots/{hashlib.md5(insight['question'].encode()).hexdigest()}.png"
                                    # image_path_2 = f"generated_plots/{hashlib.md5((insight['question'] + '_2').encode()).hexdigest()}.png"
                                    # pio.write_image(fig1, image_path_1)  # save first plot as representation\
                                    # pio.write_image(fig2, image_path_2.replace(".png", "_2.png"))  # save second plot as representation

                                    insight["image_path_1"] = image_path_1
                                    insight["image_path_2"] = image_path_2
                            except Exception as e:
                                st.warning(f"⚠️ Graph rendering failed: {e}")
        else:
            st.info("Please select a comparison insight question from the right to view the results.")

     with col_right:
        st.markdown("### 🔍 Comparison Insight Categories")

        if not compare_session.get("insight_categories"):
            try:
                preview = merged_df.to_csv(index=False)[:10000]
                llm = get_llm("groq")

                prompt = f"""
                You are provided with the following combined dataset preview:
                {preview}

                The dataset contains records from two sources:
                - Dataset 1
                - Dataset 2

                Please generate 5-6 analytical comparison insight categories.
                For each category, provide 4-6 detailed comparison-based analytical questions that compare Dataset 1 and Dataset 2.

                Example questions:
                - How do the average values of column X compare between Dataset 1 and Dataset 2?
                - Which dataset has higher variability in column Y?
                - Is there a noticeable difference in trends for column Z across datasets?

                ⚠️ IMPORTANT:
                Return strictly in the following JSON format:
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
                compare_session["insight_categories"] = categories
                st.toast("✅ Comparison insight categories loaded successfully.")
                st.rerun()

            except Exception as e:
                st.error(f"Comparison insight suggestion failed: {e}")
                compare_session["insight_categories"] = []

        for idx, category in enumerate(compare_session.get("insight_categories", [])):
            with st.expander(f"📂 {category['title']}", expanded=False):
                for question in category.get("questions", []):
                    if st.button(f"🔎 {question}", key=f"compare_insight_{idx}_{question}"):
                        try:
                            result = generate_insights(merged_df, question, "groq")

                            # Save plot if exists in result
                            import matplotlib.pyplot as plt
                            import hashlib
                            import io

                            # Check if result contains a placeholder like [Insert graph here]
                            if "[Insert graph here]" in result:
                                fig, ax = plt.subplots()
                                merged_df[merged_df.columns[0]].value_counts().plot(kind="bar", ax=ax)
                                ax.set_title("Auto-generated Plot")

                                # Save plot
                                os.makedirs("generated_plots", exist_ok=True)
                                hash_name = hashlib.md5(question.encode()).hexdigest()
                                image_path = f"generated_plots/{hash_name}.png"
                                fig.savefig(image_path)
                                plt.close(fig)

                                compare_session["insights"].append({
                                    "question": question,
                                    "result": result,
                                    "image_path_1": None,
                                    "image_path_2": None
                                })
                            else:
                                compare_session["insights"].append({
                                    "question": question,
                                    "result": result
                                })
                            st.session_state["comparison_insight_results"] = compare_session["insights"]

                            st.rerun()
                        except Exception as e:
                            st.error(f"Comparison insight generation failed: {e}")

    

    # ==================== Chatbot (Comparison Specific) ==================== #
    st.markdown("---")
    st.subheader("💬 Chat About This Comparison")

    compare_prompt = st.chat_input("Ask a question about this comparison...", key="comparison_chat_input")
    if compare_prompt:
        with st.spinner("Thinking..."):
            result = safe_llm_call(handle_user_query_dynamic, compare_prompt, merged_df, "groq", default={"response": "No response."})
        compare_session["chat_history"].append({"user": compare_prompt, "assistant": result})

    for msg in compare_session["chat_history"][::-1]:
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant"):
            st.markdown(msg["assistant"].get("response", msg["assistant"]))

    with col_right:
     st.markdown("### 📥 Export Report")
     if st.button("📄 Export Comparison Report", key="export_pdf_compare"):
        try:
            compare_session["name"] = st.session_state["current_session"]
            st.session_state["comparison_insight_results"] = compare_session.get("insights", [])
            if " vs " in compare_key:
                dataset1_name, dataset2_name = compare_key.split(" vs ")
            else:
                dataset1_name, dataset2_name = "Dataset 1", "Dataset 2"
            compare_session["dataset1_name"] = dataset1_name
            compare_session["dataset2_name"] = dataset2_name
            compare_session["comparison_insight_results"] = compare_session.get("insights", [])
            compare_session["comparison_recommendations"] = compare_session.get("recommendations", [])

            pdf_path = generate_pdf_report_comparison(compare_session, filename="comparison_summary.pdf")
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", f, file_name="comparison_summary.pdf")
        except Exception as e:
            st.error(f"Failed to export PDF: {e}")



    