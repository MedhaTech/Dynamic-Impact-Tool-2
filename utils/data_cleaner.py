def clean_data(df):
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace(r"[^\w]", "", regex=True)
    return df.dropna(how="all").reset_index(drop=True)
