# utils/sections/section2_introduction.py

from utils.llm_selector import get_llm

def generate_section2_introduction(df, model_source="groq"):
    llm = get_llm(model_source)
    prompt = f"""
    You are a business analyst. Write an introduction for a data analysis report based on the dataset below.

    Dataset Preview:
    {df.head(5).to_string()}

    Instructions:
    Include the following:
    - Background or context of the dataset
    - Scope of the analysis
    - What kind of data sources are used (based on the columns)
    - Who is the audience or stakeholder for this report

    Structure:
    - Background:
    - Scope:
    - Data Sources:
    - Stakeholders:
    """
    return llm(prompt)
