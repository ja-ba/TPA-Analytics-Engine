import pandas as pd
from tpa_analytics_engine.models.models_config import Forecast_Config
from tpa_analytics_engine.models.sklearn import forecast_sklearn


def run(
    df: pd.DataFrame, forecast_config: Forecast_Config, forecast_col_name: str = "price"
) -> pd.DataFrame:
    """A wrapper function to run the forecast on a passed data frame, according to a specified forecast configuration.

    Args:
        df (pd.DataFrame): The data frame on which to run the forecast
        config_dict (Forecast_Config): A dictionary containing the config with a key 'forecast_config'.
        forecast_col_name (str, optional): The column name of the column that should be forecasted. Defaults to "price".

    Raises:
        NotImplementedError: If the forecast config specifies an estimator class which is not implemented.

    Returns:
        pd.DataFrame: A data frame with the forecasts.
    """

    if forecast_config.use_estimator_class == "sklearn":
        return forecast_sklearn(
            df=df, forecast_config=forecast_config, forecast_col_name=forecast_col_name
        )

    else:
        raise NotImplementedError(
            f"{forecast_config.use_estimator_class} is not supported."
        )
