# # utils/sections/section7_recommendations.py

from utils.llm_selector import get_llm

# def generate_section7_recommendations(insights, model_source="groq"):
#     if not insights:
#         return []

#     llm = get_llm(model_source)
#     items = []

#     for insight in insights:
#         prompt = f"""
#         Based on the following insight, generate a recommendation table row:
#         Insight: {insight['question']} - {insight['result']}

#         Format the result as:
#         Insight | Recommended Action | Priority | Owner/Team | Timeline
        
#         """
#         try:
#             result = llm(prompt)
#             parts = result.strip().split("|")
#             if len(parts) == 5:
#                 items.append([p.strip() for p in parts])
#         except Exception:
#             continue

#     return items

# from utils.llm_selector import get_llm

# def generate_section7_recommendations(insights, model_source="groq"):
#     llm = get_llm(model_source)

#     if not insights:
#         return []

#     formatted_insights = "\n".join(
#         f"{idx+1}. {insight['question']}\n{insight['result']}\n"
#         for idx, insight in enumerate(insights)
#     )

#     prompt = f"""
# You are a senior data analyst.

# Based on the following analytical insights from a dataset, generate 3 to 5 actionable recommendations.

# For each recommendation, include:
# - Insight
# - Recommended Action
# - Priority (High/Medium/Low)
# - Owner/Team
# - Timeline

# Output in **bullet-style text format**, like:

# Insight: ...
# Recommended Action: ...
# Priority: ...
# Owner/Team: ...
# Timeline: ...

# Separate each recommendation with a line.

# Here are the insights:
# {formatted_insights}
# """

#     response = llm(prompt)
    
#     # Split the response into individual recommendations based on the line separator
#     recommendation_blocks = response.strip().split("\n----------------------------------------------------")
    
#     parsed_recs = []
#     for block in recommendation_blocks:
#         lines = block.strip().splitlines()
#         rec = {}
#         for line in lines:
#             if ":" in line:
#                 key, value = line.split(":", 1)
#                 rec[key.strip()] = value.strip()
#         if rec:
#             parsed_recs.append(rec)

#     return parsed_recs

# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from utils.llm_selector import get_llm

# llm = get_llm("groq")  # uses llama3-8b-8192

# recommendation_prompt = PromptTemplate(
#     input_variables=["insight"],
#     template="""
# You are a business analyst. Based on the following data insight, generate a structured recommendation with the following fields:

# Insight: <The core insight in one sentence>
# Recommended Action: <A specific action to take>
# Priority: <High, Medium, or Low>
# Owner/Team: <Suggest a suitable team or department to own this>
# Timeline: <Recommended timeline for implementation>

# Insight:
# {insight}

# Return the output strictly in this JSON format:
# {{
#   "insight": "...",
#   "recommended_action": "...",
#   "priority": "...",
#   "owner_team": "...",
#   "timeline": "..."
# }}
# """
# )

# recommendation_chain = LLMChain(llm=llm, prompt=recommendation_prompt)

# def generate_recommendation(insight_text: str) -> dict:
#     try:
#         response = recommendation_chain.run(insight=insight_text)
        
#         # Use eval safely to parse dict
#         rec_dict = eval(response.strip())
        
#         # Fallback if incomplete
#         keys = ["insight", "recommended_action", "priority", "owner_team", "timeline"]
#         for key in keys:
#             if key not in rec_dict:
#                 rec_dict[key] = "N/A"

#         return rec_dict

#     except Exception as e:
#         return {
#             "insight": "N/A",
#             "recommended_action": "N/A",
#             "priority": "N/A",
#             "owner_team": "N/A",
#             "timeline": "N/A"
#         }
# from utils.llm_selector import get_llm

# def generate_section7_recommendations(insights, model_source="groq"):
#     if not insights:
#         return []

#     llm = get_llm(model_source)
#     recommendations = []

#     for insight in insights:
#         question = insight.get("question", "")
#         result = insight.get("result", "")

#         prompt = f"""
#         You are a business analyst. Based on the following data insight, generate a structured recommendation with the following fields:

#          Insight: <The core insight in one sentence>
#          Recommended Action: <A specific action to take>
#          Priority: <High, Medium, or Low>
#          Owner/Team: <Suggest a suitable team or department to own this>
#          Timeline: <Recommended timeline for implementation>

#         Based on the following analytical insight, generate one actionable recommendation in the following table row format:
#         Insight | Recommended Action | Priority | Owner/Team | Timeline

#         Insight: {question}
#         Insight Result: {result}

#         ⚠️ Only return the table row as:
#         Insight | Recommended Action | Priority | Owner/Team | Timeline
#         """

#         try:
#             response = llm(prompt)
#             if hasattr(response, "content"):
#                 response = response.content.strip()
#             row_parts = [p.strip() for p in response.split("|")]

#             if len(row_parts) == 5:
#                 recommendations.append(row_parts)
#         except Exception as e:
#             print(f"Recommendation generation failed for: {question} → {e}")
#             continue

#     return recommendations
# from utils.llm_selector import get_llm

# def generate_section7_recommendations(insights, model_source="groq"):
#     if not insights:
#         return []

#     llm = get_llm(model_source)
#     items = []

#     for insight in insights:
#         prompt = f"""
# You are a business analyst.

# Based on the following analytical insight from a data report, generate a single actionable recommendation row.

# Insight:
# {insight['question']} - {insight['result']}

# Respond in this exact format (one line only, pipe-separated):
# Insight | Recommended Action | Priority (High/Medium/Low) | Owner/Team | Timeline (e.g., 2 weeks)

# Return only the row. Do not include explanations, markdown, or headings.
#         """

#         try:
#             result = llm(prompt)
#             if hasattr(result, "content"):
#                 result = result.content

#             print("🔎 Raw LLM Output:", result)  # Debug line

#             parts = result.strip().split("|")
#             if len(parts) == 5:
#                 items.append([p.strip() for p in parts])
#         except Exception as e:
#             print(f"❌ Recommendation generation failed: {e}")
#             continue

#     return items

from utils.llm_selector import get_llm

def generate_section7_recommendations(insights, model_source="groq"):
    llm = get_llm(model_source)

    if not insights:
        return []

    # Combine insights
    formatted_insights = "\n".join(
        f"{idx+1}. {insight['question']}\n{insight['result']}"
        for idx, insight in enumerate(insights)
    )

    # Prompt for LLM
    prompt = f"""
You are a senior data analyst.

Based on the following analytical insights from a dataset, generate 3 to 5 **structured recommendations**.

Each recommendation must include these 5 fields:
- Insight
- Recommended Action
- Priority (High/Medium/Low)
- Owner/Team
- Timeline

❗ Format exactly like this for each recommendation:

Insight: ...
Recommended Action: ...
Priority: ...
Owner/Team: ...
Timeline: ...

Separate each recommendation using this:
----------------------------------------------------

Here are the insights:
{formatted_insights}
"""

    try:
        response = llm(prompt)
    except Exception:
        return []

    # Parse each recommendation block
    blocks = response.strip().split("----------------------------------------------------")
    recommendations = []

    for block in blocks:
        lines = block.strip().splitlines()
        rec = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                rec[key.strip()] = value.strip()
        if rec:
            recommendations.append(rec)

    return recommendations
