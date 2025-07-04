import plotly.express as px
import pandas as pd

def visualize_from_llm_response(df, query, llm_response):
    chart_type = llm_response.get("chart_type", "bar").lower()
    x = llm_response.get("x")
    y = llm_response.get("y")
    group_by = llm_response.get("group_by")

    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x, y=y, color=group_by)
        elif chart_type == "line":
            fig = px.line(df, x=x, y=y, color=group_by)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x, y=y, color=group_by)
        elif chart_type == "box":
            fig = px.box(df, x=x, y=y, color=group_by)
        elif chart_type == "violin":
            fig = px.violin(df, x=x, y=y, color=group_by)
        elif chart_type == "area":
            fig = px.area(df, x=x, y=y, color=group_by)
        elif chart_type == "pie":
            fig = px.pie(df, names=x, values=y)
        else:
            return None, "Unsupported chart type."
        return fig, f"Generated {chart_type} chart for {x} vs {y}."
    except Exception as e:
        return None, f"Visualization failed: {str(e)}"

def visualize_comparison_overlay(df1, df2, x, y, name1, name2, chart_type):
    df1_copy = df1.copy()
    df2_copy = df2.copy()
    df1_copy["dataset"] = name1
    df2_copy["dataset"] = name2
    combined = pd.concat([df1_copy, df2_copy])

    try:
        if chart_type == "bar":
            fig = px.bar(combined, x=x, y=y, color="dataset", barmode="group")
        elif chart_type == "line":
            fig = px.line(combined, x=x, y=y, color="dataset")
        elif chart_type == "scatter":
            fig = px.scatter(combined, x=x, y=y, color="dataset")
        else:
            return None, "Unsupported chart type."
        return fig, f"{chart_type.title()} chart overlay of {name1} and {name2}."
    except Exception as e:
        return None, str(e)

def visualize_comparison_side_by_side(df1, df2, x, y, chart_type):
    try:
        fig1, fig2 = None, None
        if chart_type == "bar":
            fig1 = px.bar(df1, x=x, y=y, title="Dataset 1")
            fig2 = px.bar(df2, x=x, y=y, title="Dataset 2")
        elif chart_type == "line":
            fig1 = px.line(df1, x=x, y=y, title="Dataset 1")
            fig2 = px.line(df2, x=x, y=y, title="Dataset 2")
        elif chart_type == "scatter":
            fig1 = px.scatter(df1, x=x, y=y, title="Dataset 1")
            fig2 = px.scatter(df2, x=x, y=y, title="Dataset 2")
        return fig1, fig2
    except Exception as e:
        return None, None
