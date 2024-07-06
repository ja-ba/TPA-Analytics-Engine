from typing import Literal

import pandas as pd
from cloud_storage_wrapper.oci_access.pandas import PandasOCI
from tpa_analytics_engine.data_handler.prepare_forecast_format import add_columns
from tpa_analytics_engine.data_handler.prepare_forecast_format import Data_Config
from tpa_analytics_engine.data_handler.prepare_forecast_format import (
    filter_n_days_before,
)
from tpa_analytics_engine.data_handler.prepare_forecast_format import load_station_sorte
from tpa_analytics_engine.explorative.summaries import mean_centralize
from tpa_analytics_engine.explorative.summaries import summarize
from tpa_analytics_engine.models.make_forecast import run
from tpa_analytics_engine.models.models_config import create_forecast_config
from tpa_analytics_engine.utils import get_config


class Forecast:
    def __init__(self, config_path: str) -> None:
        """Initializes a Forecast class object, which can be used to create forecasts using the config and functionality of the package.

        Args:
            config_path (str): The path to the config YAML file.
        """
        self.config_path = config_path
        self.configDict = get_config(config_path=self.config_path)
        self.data_config = Data_Config(**self.configDict.get("data_config"))  # type: ignore
        self.pandas_connection = PandasOCI(**self.configDict.get("oci_config"))  # type: ignore
        self.forecast_config = create_forecast_config(self.configDict)
        self.df: pd.DataFrame = pd.DataFrame()

    def load_df(self, station: str, sorte: str) -> None:
        """Loads the df for passed station and sorte

        Args:
            station (str): The short id of the station to load.
            sorte (str): The type of gas for which to load the price
        """
        self.df = add_columns(
            load_station_sorte(
                pandas_connection=self.pandas_connection,
                data_config=self.data_config,
                station=station,
                sorte=sorte,
                add_pred=False,
            )
        )

    def create_forecast(self) -> pd.DataFrame:
        """Creates a forecast for the previously loaded df.

        Raises:
            ValueError: If self.df is empty, i.e. no df was loaded.

        Returns:
            pd.DataFrame: The data frame with the forecast.
        """
        if len(self.df) == 0:
            raise ValueError("No df is loaded in the object.")
        else:
            currentDF = filter_n_days_before(
                df=self.df, n_before=self.forecast_config.n_before
            )
        return run(df=currentDF, forecast_config=self.forecast_config)

    def create_summaries(
        self, groupCol: Literal["day_of_week", "hour", "trend"]
    ) -> pd.Series:
        """Summarises the "price" column by groupCol.

        Args:
            groupCol (Literal['day_of_week', 'hour', 'trend']): The time column by which to group by.

        Raises:
            ValueError: If self.df is empty, i.e. no df was loaded.

        Returns:
            pd.Series: A pd.Series with the grouped prices.
        """
        if len(self.df) == 0:
            raise ValueError("No df is loaded in the object.")
        else:
            return mean_centralize(
                summarize(df=self.df, groupCol=groupCol, aggCol="price")
            )
