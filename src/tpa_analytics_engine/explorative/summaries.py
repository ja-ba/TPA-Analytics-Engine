import pandas as pd


def summarize(df: pd.DataFrame, groupCol: str, aggCol: str) -> pd.Series:
    """Groups a df by a groupby column: groupCol for an aggregation column: aggCol.

    Args:
        df (pd.DataFrame): The df to group.
        groupCol (str): The groupby column by which the values of the aggregation  will be grouped.
        aggCol (str): The aggregation column, these values will be aggregated.

    Raises:
        ValueError: If groupCol is not in the df.
        ValueError: If aggCol is not in the df.

    Returns:
        Series: The series with the grouped values.
    """
    if groupCol not in df:
        raise ValueError(f"The groupby column: {groupCol} is not in the df.")
    if aggCol not in df:
        raise ValueError(f"The aggregation column: {aggCol} is not in the df.")

    return df.groupby(groupCol)[aggCol].mean()


def mean_centralize(series: pd.Series) -> pd.Series:
    """Centralizes a series according to the mean.

    Args:
        series (pd.Series): The series to centralize.

    Returns:
        pd.Series: The centralized series.
    """
    return series - series.mean()
