import datetime
from typing import Literal

import numpy as np
import pandas as pd
from cloud_storage_wrapper.oci_access.pandas import PandasOCI
from pydantic import BaseModel


# Pydantic Base Class for Data
class Data_Config(BaseModel):
    """A pydantic class to specify the data configuration.
    The configuration specifies the path to the df, the used format and the date column containing dates and times.
    """

    df_path: str
    df_format: Literal["ftr", "parquet"]
    date_column: str


def load_station_sorte(
    pandas_connection: PandasOCI,
    data_config: Data_Config,
    station: str,
    sorte: str,
    add_pred: bool = True,
) -> pd.DataFrame:
    """This function loads

    Args:
        data_config (Data_Config): The data configuration specifying the relevant information on which data to use.
        station (str): The short id of the station to load.
        sorte (str): The type of gas for which to load the price
        add_pred (bool, optional): A flag whether to add a prediction time frame to the df. Defaults to True.

    Returns:
        pd.DataFrame: The df for the required station and gas_type.
    """
    # Download the df based on data_config:
    df = (
        pandas_connection.retrieve_df(
            path=data_config.df_path,
            df_format=data_config.df_format,
            columns=[data_config.date_column, f"{sorte}_{station}"],
        )
        .rename(columns={f"{sorte}_{station}": "price"})
        .dropna()
    )

    # If add_pred is true, then add the times of the same day last week with a price of 0 --> this price will be predicted later
    if add_pred:
        current_date = datetime.date.today()
        date_7_days_ago = current_date - datetime.timedelta(days=7)
        filtered_df = df[df[data_config.date_column].dt.date == date_7_days_ago].copy()
        filtered_df[data_config.date_column] = filtered_df[
            data_config.date_column
        ].apply(
            lambda x: x.replace(
                year=current_date.year, month=current_date.month, day=current_date.day
            )
        )
        filtered_df["price"] = 0
        df = pd.concat([df, filtered_df], ignore_index=True)

    return df


def add_columns(df: pd.DataFrame) -> pd.DataFrame:
    """This function adds date features to the df:
        - day_of_week
        - hour
        - trend
        - avg_daily_price for the last 1,2,3 days
        - is_last ( a flag flagging the last date in the df)

    Args:
        df (pd.DataFrame): A data frame as produced by load_station_sorte().

    Returns:
        pd.DataFrame: The data frame with the added features.
    """

    # Create day and trend columns
    df["day_of_week"] = df["Day_Hours"].dt.dayofweek
    df["hour"] = df["Day_Hours"].dt.hour + (
        (df["Day_Hours"].dt.minute.astype("float") // 30) / 2
    )
    df["hour_format"] = df["Day_Hours"].dt.time.astype(str).str[:5]
    df["Day"] = df["Day_Hours"].dt.date
    df["trend"] = df["Day"].apply(lambda x: x.toordinal())
    df["trend"] = df["trend"] - df["trend"].min()
    df["week"] = df["Day_Hours"].astype("datetime64[ns]").dt.strftime("%Y-%W")

    # Calculate the average prices of the 3 days before
    avg_daily_price = df.groupby("Day")[["price"]].mean().reset_index()
    avg_daily_price = avg_daily_price.sort_values(by="Day")

    avg_daily_price["avg_daily_price_lag1"] = avg_daily_price["price"].shift(1).bfill()
    avg_daily_price["avg_daily_price_lag2"] = avg_daily_price["price"].shift(2).bfill()
    avg_daily_price["avg_daily_price_lag3"] = avg_daily_price["price"].shift(3).bfill()
    del avg_daily_price["price"]

    # Merge the calculated averages to df
    df = df.merge(avg_daily_price, on="Day", how="inner")

    # Determine the last day and flag it as column "is_last"
    df["is_last"] = np.where(df["Day"] == df["Day"].max(), 1, 0)

    return df


def filter_n_days_before(df: pd.DataFrame, n_before: int) -> pd.DataFrame:
    """A function filtering the input df to n days before the last date.
    This is needed to reduce the training dates, since more training dates don't produce better results but increase serving time.

    Args:
        df (pd.DataFrame): A data frame as produced by load_station_sorte().
        n_before (int): The number of days to include before the last date.

    Returns:
        pd.DataFrame: The filtered input df.
    """
    # Create 'Day' column if not existant
    if "Day" not in df:
        df["Day"] = df["Day_Hours"].dt.date

    # Reduce by n_before days before max_Date
    max_Date = df["Day"].max()
    min_Date = max_Date - datetime.timedelta(days=n_before - 1)
    df = df[(df["Day"] >= min_Date) & (df["Day"] <= max_Date)].copy()

    return df
