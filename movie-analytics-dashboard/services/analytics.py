# services/analytics.py

def apply_filters(df, filters):
    year_min, year_max = filters["year_range"]
    min_votes = filters["min_votes"]

    df_filtered = df[
        (df["year"] >= year_min) &
        (df["year"] <= year_max) &
        (df["num_votes"] >= min_votes)
    ]

    return df_filtered