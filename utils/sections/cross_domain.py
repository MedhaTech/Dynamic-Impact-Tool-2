# utils/sections/section6_cross_domain.py

import pandas as pd
from utils.llm_selector import get_llm

def generate_section6_cross_domain(df: pd.DataFrame, model_source="groq") -> str:
    llm = get_llm(model_source)

    preview_str = df.to_string()
    describe_str = df.describe(include="all").to_string()

    prompt = f"""
You are generating the **Cross-Domain Insights** section of a data report.

This section should:
- Identify correlations or patterns across different domains or columns
- Summarize combined or compounding effects observed
- Offer holistic interpretations useful for business or operations

Here’s a preview of the dataset:
{preview_str}

And some descriptive stats:
{describe_str}

Write 2-3 paragraphs highlighting cross-domain insights in formal report style.
"""

    try:
        return llm(prompt)
    except Exception as e:
        return f"⚠️ LLM generation failed: {e}"
