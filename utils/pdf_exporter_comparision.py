# from fpdf import FPDF
# from fpdf.enums import XPos, YPos
# import os
# from datetime import datetime
# from utils.sections.summary import generate_section1_summary
# from utils.sections.introduction import generate_section2_introduction
# from utils.sections.data_overview import generate_section3_data_overview
# from utils.sections.methodology import generate_section4_methodology
# from utils.sections.cross_domain import generate_section6_cross_domain
# from utils.sections.recommendation import generate_section7_recommendations
# import textwrap
# import re
# import streamlit as st

# def safe_multicell(pdf, text, width=180, font_size=12):
#     import textwrap
#     import re

#     pdf.set_font("DejaVu", "", font_size)

    
#     text = re.sub(r"(?i)^analytical insight:.*$", "", text, flags=re.MULTILINE)  
#     text = re.sub(r"={3,}|-{3,}", "", text)  
#     text = re.sub(r"\*\*+", "", text)  
#     text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)  

   
#     text = text.replace("🚀", "").replace("🧑", "").replace("🤖", "")
    
    
#     paragraphs = text.split("\n")
#     for para in paragraphs:
#         para = para.strip()
#         if para:
#             wrapped_lines = textwrap.wrap(para, width=90)
#             for line in wrapped_lines:
#                 pdf.cell(0, 10, line, ln=True)
#             pdf.ln(2)

# def generate_comparison_pdf_report(session, filename="comparison_report.pdf", model_source="groq"):
#     df1 = session.get("df1")
#     df2 = session.get("df2")
#     dataset1_name = session.get("dataset1_name", "Dataset A")
#     dataset2_name = session.get("dataset2_name", "Dataset B")
#     insights = session.get("comparison_insight_results", [])  # You should store these in session
#     chat_history = session.get("chat_history", [])

#     pdf = FPDF()
#     font_path = os.path.join("assets", "fonts", "DejaVuSans.ttf")
#     pdf.add_font("DejaVu", "", font_path)
#     pdf.add_font("DejaVu", "B", font_path)
#     pdf.set_font("DejaVu", "", 14)
#     section_pages = []

#     # === COVER PAGE ===
#     pdf.add_page()
#     pdf.set_font("DejaVu", "B", 20)
#     pdf.cell(0, 20, "Comparison Report", ln=True, align="C")
#     pdf.set_font("DejaVu", "", 16)
#     pdf.cell(0, 10, f"{dataset1_name} vs {dataset2_name}", ln=True, align="C")
#     pdf.ln(10)
#     pdf.set_font("DejaVu", "", 12)
#     pdf.cell(0, 10, f"Date: {datetime.now().strftime('%d %B %Y')}", ln=True, align="C")

#     # === INDEX PAGE ===
#     pdf.add_page()
#     section_pages.append(("Index", pdf.page_no()))

#     # === SECTION 1–3 FOR BOTH DATASETS SEPARATELY ===
#     from utils.sections.summary import generate_section1_summary
#     from utils.sections.introduction import generate_section2_introduction
#     from utils.sections.data_overview import generate_section3_data_overview
#     from utils.sections.methodology import generate_section4_methodology
#     from utils.sections.cross_domain import generate_section6_cross_domain
#     from utils.sections.recommendation import generate_section7_recommendations
    

#     for df, name, label in [(df1, dataset1_name, "A"), (df2, dataset2_name, "B")]:
#         # === SECTION 1 ===
#         try:
#             pdf.add_page()
#             section_pages.append((f"Executive Summary ({label})", pdf.page_no()))
#             summary_text = generate_section1_summary(df, model_source)
#             pdf.set_font("DejaVu", "B", 16)
#             pdf.cell(0, 10, f"1. Executive Summary – {name}", ln=True)
#             pdf.set_font("DejaVu", "", 12)
#             safe_multicell(pdf, summary_text)
#         except Exception as e:
#             st.error(f"Error in Summary ({label}): {e}")

#         # === SECTION 2 ===
#         pdf.add_page()
#         section_pages.append((f"Introduction ({label})", pdf.page_no()))
#         pdf.set_font("DejaVu", "B", 16)
#         pdf.cell(0, 10, f"2. Introduction – {name}", ln=True)
#         intro_text = generate_section2_introduction(df, model_source)
#         pdf.set_font("DejaVu", "", 12)
#         safe_multicell(pdf, intro_text)

#         # === SECTION 3 ===
#         pdf.add_page()
#         section_pages.append((f"Data Overview ({label})", pdf.page_no()))
#         pdf.set_font("DejaVu", "B", 16)
#         pdf.cell(0, 10, f"3. Data Overview – {name}", ln=True)
#         overview_text = generate_section3_data_overview(df, model_source)
#         pdf.set_font("DejaVu", "", 12)
#         safe_multicell(pdf, overview_text)

#     # === SECTION 4: Methodology ===
#     pdf.add_page()
#     section_pages.append(("Methodology", pdf.page_no()))
#     pdf.set_font("DejaVu", "B", 16)
#     pdf.cell(0, 10, "4. Methodology", ln=True)
#     method_text = generate_section4_methodology(df1, model_source)  # can merge both or just df1
#     pdf.set_font("DejaVu", "", 12)
#     safe_multicell(pdf, method_text)

#     # === SECTION 5: Detailed Comparison Insights ===
#     pdf.add_page()
#     section_pages.append(("Detailed Comparison Insights", pdf.page_no()))
#     pdf.set_font("DejaVu", "B", 16)
#     pdf.cell(0, 10, "5. Detailed Comparison Insights", ln=True)
#     if insights:
#         for idx, insight in enumerate(insights, start=1):
#             pdf.set_font("DejaVu", "B", 14)
#             pdf.ln(5)
#             pdf.multi_cell(0, 10, f"5.{idx} Insight: {insight['question']}")
#             pdf.set_font("DejaVu", "", 12)
#             safe_multicell(pdf, insight["result"])
#     else:
#         pdf.multi_cell(0, 10, "No comparison insights were generated.")

#     # === SECTION 6: Cross-Domain Insights ===
#     pdf.add_page()
#     section_pages.append(("Cross-Domain Insights", pdf.page_no()))
#     cross_text = generate_section6_cross_domain(df1, model_source)
#     pdf.set_font("DejaVu", "B", 16)
#     pdf.cell(0, 10, "6. Cross-Domain Insights", ln=True)
#     pdf.set_font("DejaVu", "", 12)
#     safe_multicell(pdf, cross_text)

#     # === SECTION 7: Recommendations (Based on comparison insights) ===
    # pdf.add_page()
    # section_pages.append(("Recommendations & Actionable Items", pdf.page_no()))
    # pdf.set_font("DejaVu", "B", 16)
    # pdf.cell(0, 10, "7. Recommendations & Actionable Items", ln=True)
    # pdf.ln(5)
    # recommendations = generate_section7_recommendations(insights, model_source)

    # if recommendations:
    #     pdf.set_font("DejaVu", "", 12)
    #     for idx, rec in enumerate(recommendations, start=1):
    #         text = (
    #             f"🔍 Insight: {rec.get('Insight', 'N/A')}\n"
    #             f"💡 Recommended Action: {rec.get('Recommended Action', 'N/A')}\n"
    #             f"🔥 Priority: {rec.get('Priority', 'N/A')}\n"
    #             f"👥 Owner/Team: {rec.get('Owner', 'N/A')}\n"
    #             f"🕒 Timeline: {rec.get('Timeline', 'N/A')}\n"
    #             "----------------------------------------------------\n"
    #         )
    #         safe_multicell(pdf, text)
    # else:
    #     pdf.set_font("DejaVu", "", 12)
    #     pdf.multi_cell(0, 10, "No recommendations generated.")

#     # === INDEX PAGE BACKFILL ===
#     pdf.page = 2  # second page
#     pdf.set_font("DejaVu", "B", 18)
#     pdf.cell(0, 10, "Index", ln=True)
#     pdf.ln(5)
#     pdf.set_font("DejaVu", "B", 12)
#     col_widths = [15, 100, 30]
#     headers = ["S.No", "Section Title", "Page No."]
#     for i, header in enumerate(headers):
#         pdf.cell(col_widths[i], 10, header, border=1, align="C")
#     pdf.ln()
#     pdf.set_font("DejaVu", "", 12)
#     for idx, (title, page) in enumerate(section_pages[1:], 1):  # skip Index itself
#         pdf.cell(col_widths[0], 10, str(idx), border=1, align="C")
#         pdf.cell(col_widths[1], 10, title, border=1)
#         pdf.cell(col_widths[2], 10, str(page), border=1, align="C")
#         pdf.ln()

#     # === SAVE PDF ===
#     os.makedirs("exports", exist_ok=True)
#     output_path = os.path.join("exports", filename)
#     pdf.output(output_path)
#     return output_path


from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import datetime
from utils.sections.summary import generate_section1_summary
from utils.sections.introduction import generate_section2_introduction
from utils.sections.data_overview import generate_section3_data_overview
from utils.sections.methodology import generate_section4_methodology
from utils.sections.cross_domain import generate_section6_cross_domain
from utils.sections.recommendation import generate_section7_recommendations
# from utils.pdf_utils import safe_multicell, draw_markdown_table, clean_insight_text
import streamlit as st
import re
class CustomPDF(FPDF):
    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("DejaVu", "I", 10)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def clean_insight_text(text):
    # Remove markdown tables completely
    text = re.sub(
        r"(\n\|.+?\|\n\|[-| :]+\|\n(?:\|.*?\|\n?)+)",
        "", text, flags=re.MULTILINE
    )
    # Remove unwanted lines like Analytical Insight or ===
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or "Analytical Insight" in stripped or re.match(r"=+", stripped):
            continue
        cleaned_lines.append(stripped)
    return "\n".join(cleaned_lines)


def safe_multicell(pdf, text, width=180, font_size=12):
    import textwrap
    import re

    pdf.set_font("DejaVu", "", font_size)

    # --- Clean up unwanted content ---
    text = re.sub(r"(?i)^analytical insight:.*$", "", text, flags=re.MULTILINE)  # remove "Analytical Insight: ..." line
    text = re.sub(r"={3,}|-{3,}", "", text)  # remove "===" or "---" separators
    text = re.sub(r"\*\*+", "", text)  # remove bold markdown
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)  # remove markdown headers like ###

    # Optional cleanup
    text = text.replace("🚀", "").replace("🧑", "").replace("🤖", "")
    
    # --- Render cleaned text ---
    paragraphs = text.split("\n")
    for para in paragraphs:
        para = para.strip()
        if para:
            wrapped_lines = textwrap.wrap(para, width=90)
            for line in wrapped_lines:
                pdf.cell(0, 10, line, ln=True)
            pdf.ln(2)

def draw_markdown_table(pdf, markdown_text):
    lines = markdown_text.strip().split("\n")
    table_lines = [line for line in lines if "|" in line and "---" not in line]

    if not table_lines:
        return False  # No table detected

    # Clean and split table rows
    rows = [line.strip().strip("|").split("|") for line in table_lines]
    col_width = 180 // len(rows[0])
    pdf.set_font("DejaVu", "", 11)
    

    for row in rows:
        for cell in row:
            pdf.cell(col_width, 10, cell.strip(), border=1)
        pdf.ln()
    pdf.ln(5)
    return True

# def render_recommendation_table(pdf, rec, idx):
#     # col_width = pdf.w / 4.5
#     page_width = pdf.w - 2 * pdf.l_margin  # total printable width
#     col_width = page_width / 5  # 5 columns: Insight, Action, Priority, Owner/Team, Timeline

#     pdf.set_font("DejaVu", "B", 12)
#     pdf.cell(0, 10, f"Recommendation {idx}", ln=True)
#     pdf.set_font("DejaVu", "", 12)

#     headers = ["Insight", "Action", "Priority", "Owner/Team", "Timeline"]
#     values = [
#         rec.get("insight", "N/A"),
#         rec.get("recommended_action", "N/A"),
#         rec.get("priority", "N/A"),
#         rec.get("owner_team", "N/A"),
#         rec.get("timeline", "N/A")
#     ]
def render_recommendation_table(pdf, rec, idx):
    page_width = pdf.w - 2 * pdf.l_margin
    col_width = page_width / 5

    headers = ["Insight", "Action", "Priority", "Owner/Team", "Timeline"]
    values = [
        rec.get("insight", "N/A"),
        rec.get("recommended_action", "N/A"),
        rec.get("priority", "N/A"),
        rec.get("owner_team", "N/A"),
        rec.get("timeline", "N/A")
    ]

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, f"Recommendation {idx}", ln=True)
    pdf.set_font("DejaVu", "", 11)

    # Header row
    for header in headers:
        pdf.cell(col_width, 10, header, border=1)
    pdf.ln()

    # Values row
    for value in values:
        pdf.multi_cell(col_width, 10, str(value), border=1, max_line_height=pdf.font_size)
    pdf.ln(5)

    # Render headers
    for header in headers:
        pdf.cell(col_width, 10, header, border=1)
    pdf.ln()

    # Render values
    for value in values:
        pdf.cell(col_width, 10, str(value), border=1)
    pdf.ln(10)


from utils.sections.recommendation import generate_section7_recommendations



def add_section_7(pdf, insights, section_pages, model_source="groq"):
    pdf.add_page()
    section_pages.append(("Recommendations & Actionable Items", pdf.page_no()))  # ✅ Add to index

    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "7. Recommendations & Actionable Items", ln=True)

    recommendations = generate_section7_recommendations(insights, model_source)

    if not recommendations:
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 10, "No recommendations could be generated from the insights.")
        return

    # Check if table is structured
    required_keys = {"Insight", "Recommended Action", "Priority", "Owner/Team", "Timeline"}
    structured = all(required_keys.issubset(set(rec.keys())) for rec in recommendations)

    if structured:
        # Prepare and render table
        table_data = [
            ["Insight", "Recommended Action", "Priority", "Owner/Team", "Timeline"],
            *[[
                rec.get("Insight", ""),
                rec.get("Recommended Action", ""),
                rec.get("Priority", ""),
                rec.get("Owner/Team", ""),
                rec.get("Timeline", "")
            ] for rec in recommendations]
        ]
        render_recommendation_table(pdf, table_data)
    else:
        # Fallback: bullet-style layout
        pdf.set_font("DejaVu", "", 12)
        for idx, rec in enumerate(recommendations, start=1):
            pdf.set_font("DejaVu", "B", 12)
            pdf.multi_cell(0, 10, f"\nRecommendation {idx}", ln=True)
            pdf.set_font("DejaVu", "", 12)

            if "Insight" in rec:
                pdf.multi_cell(0, 10, f"Insight: {rec.get('Insight')}")
            if "Recommended Action" in rec:
                pdf.multi_cell(0, 10, f"Recommended Action: {rec.get('Recommended Action')}")
            if "Priority" in rec:
                pdf.multi_cell(0, 10, f"Priority: {rec.get('Priority')}")
            if "Owner/Team" in rec:
                pdf.multi_cell(0, 10, f"Owner/Team: {rec.get('Owner/Team')}")
            if "Timeline" in rec:
                pdf.multi_cell(0, 10, f"Timeline: {rec.get('Timeline')}")
            pdf.ln(3)




def generate_pdf_report_comparison(compare_session, filename="comparison_report.pdf", model_source="groq"):
    df1 = compare_session["df1"]
    df2 = compare_session["df2"]
    name1 = compare_session["dataset1_name"]
    name2 = compare_session["dataset2_name"]
    insights = compare_session.get("insights", [])

    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    font_path = os.path.join("assets", "fonts", "DejaVuSans.ttf")
    bold_font_path = os.path.join("assets", "fonts", "DejaVuSans-Bold.ttf")
    italic_font_path = os.path.join("assets", "fonts", "DejaVuSans-Oblique.ttf")
    pdf.add_font("DejaVu", "I", italic_font_path)

    pdf.add_font("DejaVu", "", font_path)
    pdf.add_font("DejaVu", "B", bold_font_path)
    pdf.set_font("DejaVu", size=12)

    section_pages = []

    # === COVER PAGE ===
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 20)
    pdf.cell(0, 20, "Dynamic Dataset Analysis Report", ln=True, align="C")
    pdf.set_font("DejaVu", "", 16)
    pdf.cell(0, 10, "Generated by Dynamic Impact Tool", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%d %B %Y')}", ln=True, align="C")
    pdf.cell(0, 10, f"Datasets: {name1} vs {name2}", ln=True, align="C")

    # === INDEX PAGE ===
    pdf.add_page()
    index_start_page = pdf.page_no()
    section_pages.append(("Index", index_start_page))

    # === SECTION 1: Executive Summary ===
    pdf.add_page()
    section_pages.append(("Executive Summary", pdf.page_no()))
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "1. Executive Summary", ln=True)
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(0, 10, f"Summary for {name1}", ln=True)
    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, generate_section1_summary(df1, model_source))
    pdf.ln(4)
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(0, 10, f"Summary for {name2}", ln=True)
    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, generate_section1_summary(df2, model_source))

    # === SECTION 2: Introduction ===
    pdf.add_page()
    section_pages.append(("Introduction", pdf.page_no()))
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "2. Introduction", ln=True)
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(0, 10, f"Introduction for {name1}", ln=True)
    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, generate_section2_introduction(df1, model_source))
    pdf.ln(4)
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(0, 10, f"Introduction for {name2}", ln=True)
    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, generate_section2_introduction(df2, model_source))

    # === SECTION 3: Data Overview ===
    pdf.add_page()
    section_pages.append(("Data Overview", pdf.page_no()))
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "3. Data Overview", ln=True)
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(0, 10, f"Overview for {name1}", ln=True)
    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, generate_section3_data_overview(df1, model_source))
    pdf.ln(4)
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(0, 10, f"Overview for {name2}", ln=True)
    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, generate_section3_data_overview(df2, model_source))

    # === SECTION 4: Methodology ===
    pdf.add_page()
    section_pages.append(("Methodology", pdf.page_no()))
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "4. Methodology", ln=True)
    safe_multicell(pdf, generate_section4_methodology(df1, model_source))

    # === SECTION 5: Detailed Comparison Insights ===
    pdf.add_page()
    section_pages.append(("Detailed Comparison Insights", pdf.page_no()))
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "5. Detailed Comparison Insights", ln=True)
    if insights:
        for idx, insight in enumerate(insights, start=1):
            if idx > 1:
                pdf.add_page()
            pdf.set_font("DejaVu", "B", 14)
            pdf.multi_cell(0, 10, f"5.{idx} Insight: {insight['question']}")
            pdf.set_font("DejaVu", "", 12)
            result_text = insight["result"]
            table_rendered = draw_markdown_table(pdf, result_text)
            cleaned_text = clean_insight_text(result_text)
            safe_multicell(pdf, cleaned_text)
            image_path1 = insight.get("image_path_1")
            image_path2 = insight.get("image_path_2")
            for img_path in [image_path1, image_path2]:
                if img_path and os.path.exists(img_path):
                    try:
                     pdf.ln(3)
                     pdf.image(img_path, w=160)
                     pdf.ln(5)
                    except Exception as e:
                     print(f"Couldn't embed image for Insight {idx}: {e}")
            pdf.ln(5)

            # if image_path1 and isinstance(image_path1, str) and os.path.exists(image_path1):
            #  pdf.ln(3)
            #  try:
            #     pdf.image(image_path1, w=160)
            #     pdf.ln(5)
            #  except Exception as e:
            #     print(f"Couldn't embed image for Insight {idx}: {e}")

            
            # if image_path2 and isinstance(image_path2, str) and os.path.exists(image_path2):
            #     pdf.ln(3)
            #     try:
            #         pdf.image(image_path2, w=160)
            #         pdf.ln(5)
            #     except Exception as e:
            #         print(f"Couldn't embed second image for Insight {idx}: {e}")

            # pdf.ln(5)
    else:
        safe_multicell(pdf, "No insights generated.")

    # === SECTION 6: Cross-Domain Insights ===
    try:
        cross_text = generate_section6_cross_domain(df1, model_source)
        pdf.add_page()
        section_pages.append(("Cross-Domain Insights", pdf.page_no()))
        pdf.set_font("DejaVu", "B", 16)
        pdf.cell(0, 10, "6. Cross-Domain Insights", ln=True)
        pdf.set_font("DejaVu", "", 12)
        safe_multicell(pdf, cross_text)
    except Exception as e:
        if "tokens" in str(e).lower():
            st.warning("Skipping Cross-Domain Insights due to token limit error.")
        else:
            raise

    
    # SECTION 7 – Recommendations & Actionable Items


    recommendations = generate_section7_recommendations(insights, model_source)
    pdf.add_page()
    section_pages.append(("Recommendations & Actionable Items", pdf.page_no()))
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "7. Recommendations & Actionable Items", ln=True)
    pdf.ln(5)

    if recommendations:
     pdf.set_font("DejaVu", "", 12)
     for idx, rec in enumerate(recommendations, start=1):
        text = (
            f"Insight: {rec.get('Insight', 'N/A')}\n"
            f"Recommended Action: {rec.get('Recommended Action', 'N/A')}\n"
            f"Priority: {rec.get('Priority', 'N/A')}\n"
            f"Owner/Team: {rec.get('Owner', 'N/A')}\n"
            f"Timeline: {rec.get('Timeline', 'N/A')}\n"
            "----------------------------------------------------\n"
        )
        safe_multicell(pdf, text)
    else:
     pdf.set_font("DejaVu", "", 12)
     pdf.multi_cell(0, 10, "No recommendations were generated.")




    # try:
    # #  pdf.add_page()
    # #  section_pages.append(("Recommendations & Actionable Items", pdf.page_no()))
    # #  pdf.set_font("DejaVu", "B", 16)
    # #  pdf.cell(0, 10, "7. Recommendations & Actionable Items", ln=True)

    # #  pdf.set_font("DejaVu", "", 12)
    #  insights = compare_session.get("comparison_insight_results", [])
    #  add_section_7(pdf, insights,section_pages, model_source="groq")

    # #  recommendations = generate_section7_recommendations(insights, model_source="groq")
    # #  if recommendations:
    # #     render_recommendation_table(pdf, recommendations)
    # #  else:
    # #     pdf.multi_cell(0, 10, "No recommendations could be generated from the insights.")

    # except Exception as e:
    #  print(f"⚠️ Skipped Section 7 due to error: {e}")


    






    # pdf.add_page()
    # section_pages.append(("Recommendations & Actionable Items", pdf.page_no()))
    # pdf.set_font("DejaVu", "B", 16)
    # pdf.cell(0, 10, "7. Recommendations & Actionable Items", ln=True)
    # pdf.ln(5)
    # recommendations = generate_section7_recommendations(insights, model_source)

    # if recommendations:
    #     pdf.set_font("DejaVu", "", 12)
    #     for idx, rec in enumerate(recommendations, start=1):
    #         render_recommendation_table(pdf, rec, idx)
    # else:
    #     pdf.set_font("DejaVu", "", 12)
    #     pdf.multi_cell(0, 10, "No recommendations generated.")

    pdf.page = 2  # Set to index page (2nd page)
    pdf.set_xy(10, 20)
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Index", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(20, 10, "S.No", border=1)
    pdf.cell(110, 10, "Section Title", border=1)
    pdf.cell(30, 10, "Page No.", border=1, ln=True)
    pdf.set_font("DejaVu", "", 12)
    for i, (title, page) in enumerate(section_pages[1:], start=1):  # skip index
        pdf.cell(20, 10, str(i), border=1)
        pdf.cell(110, 10, title, border=1)
        pdf.cell(30, 10, str(page), border=1, ln=True)

    # === Export PDF ===
    os.makedirs("exports", exist_ok=True)
    path = os.path.join("exports", filename)
    pdf.output(path)
    return path

