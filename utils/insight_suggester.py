import json
from utils.llm_selector import get_llm
import streamlit as st
# def generate_insight_suggestions(csv_data, model_source="groq"):
#     llm = get_llm(model_source)

#     # Truncate CSV to max ~2048 characters
#     preview = csv_data[:2048]

#     prompt = f"""You are an AI data analyst. Given this CSV preview, suggest 3 insights in JSON.

# CSV:
# {preview}

# Respond ONLY in this exact JSON format:
# [
#   {{ "title": "..." }},
#   {{ "title": "..." }},
#   {{ "title": "..." }}
# ]
# """

#     response = llm(prompt).strip()

#     try:
#         return json.loads(response)
#     except json.JSONDecodeError:
#         from utils.json_utils import extract_json_list
#         suggestions = extract_json_list(response)
#         if suggestions:
#             return suggestions
#         raise ValueError(f"Failed to parse JSON. Raw response: {response}")


def generate_insight_suggestions(preview_data, model_source="groq"):
    """
    Generate categorized insight suggestions using the selected LLM.
    Returns a list of categories, each with a list of questions.
    """
    llm = get_llm(model_source)

    prompt = f"""
    I have the following dataset preview:
    {preview_data}

    Please provide 5-6 high-level analytical categories (like Trend Analysis, Anomaly Detection, Category Comparison, etc.)
    For each category, suggest 4-6 detailed analytical questions that could uncover insights from this data.

    Return the response strictly in this JSON format:
    [
        {{"title": "Category Name", "questions": ["Question 1", "Question 2", "Question 3"]}},
        ...
    ]
    """

    try:
        response = llm(prompt)
        suggestions = eval(response)  # If response is a pure Python JSON list
        return suggestions
    except Exception as e:
        
        print(f"Insight suggestion failed: {e}")
        # Fallback in case of LLM failure
        return [
            {
                "title": "Trend Analysis",
                "questions": [
                    "What is the trend of sales over time?",
                    "Which product is growing the fastest?",
                    "Is there a seasonal pattern in the data?"
                ]
            },
            {
                "title": "Anomaly Detection",
                "questions": [
                    "Are there any outliers in sales?",
                    "Are there unusual spikes or drops?",
                    "Which data points deviate from the norm?"
                ]
            },
            {
                "title": "Category Comparison",
                "questions": [
                    "Which category performs the best?",
                    "Which category has the highest variance?",
                    "How does performance vary across categories?"
                ]
            }
        ]






def generate_insights(df, title, model_source="groq"):
    llm = get_llm(model_source)

    # Limit preview to 10 rows max and truncate to 2048 characters
    preview = df.head(10).to_csv(index=False)[:2048]

    prompt = f"""You are a data analyst. Based on the dataset and the selected insight title, generate an analytical insight.

Title: {title}

CSV Preview:
{preview}

Respond in markdown format with your full analysis.
"""

    return llm(prompt)






def generate_comparison_insights(df1, df2, model_source="groq"):
    llm = get_llm(model_source)

    sample1 = df1.head(10).to_csv(index=False)[:1024]
    sample2 = df2.head(10).to_csv(index=False)[:1024]

    prompt = f"""You are a data analyst. Given these two datasets, suggest 3 insightful comparisons a user may want to explore.

Dataset 1:
{sample1}

Dataset 2:
{sample2}

Respond in JSON format:
[
  {{ "title": "...", "description": "..." }},
  ...
]
"""

    response = llm(prompt).strip()

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        from utils.json_utils import extract_json_list
        return extract_json_list(response)






import json
from utils.llm_selector import get_llm
from utils.json_utils import extract_json_list  # You’ll add this next

def generate_comparison_insights(df1, df2, model_source="groq"):
    llm = get_llm(model_source)

    prompt = f"""You are a data analyst. Given two datasets (CSV previews), suggest 3 insightful comparisons.

Dataset 1:
{df1.head(10).to_csv(index=False)}

Dataset 2:
{df2.head(10).to_csv(index=False)}

Respond ONLY in JSON like:
[
  {{ "title": "Insight 1", "description": "..." }},
  ...
]
"""

    response = llm(prompt).strip()

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # try to extract JSON manually from partial responses
        return extract_json_list(response)
