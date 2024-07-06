import pandas as pd
from tpa_analytics_engine.models.models_config import Estimator_Config
from tpa_analytics_engine.models.models_config import estimator_dict
from tpa_analytics_engine.models.models_config import Forecast_Config


def forecast_sklearn(
    df: pd.DataFrame,
    forecast_config: Forecast_Config,
    forecast_col_name: str = "price",
) -> pd.DataFrame:
    """Forecasts the forecast_col_name(default 'price') column in df using the estimator_config.

    Args:
        df (pd.DataFrame): The df on which to forecast. This df must contain the is_last column.
        forecast_config (Forecast_Config): The forecast configuration specifying the details of the forecast estimator.
        forecast_col_name (str, optional): The name of the column to forecast. Defaults to "price".

    Returns:
        pd.DataFrame: A df where rows with is_last==1 contain the forecast values.
    """
    # Get the needed estimator_dict
    current_estimator: Estimator_Config = forecast_config.estimators.get(
        forecast_config.use_estimator_class, {}
    ).get(
        forecast_config.use_estimator
    )  # type: ignore
    # Get the current_estimator_class from the estimator_dict
    current_estimator_class = estimator_dict.get(
        forecast_config.use_estimator_class, {}
    ).get(current_estimator.estimator_type)
    # Create the estimator object from the current_estimator_class
    current_estimator_object = current_estimator_class(
        **current_estimator.estimator_kwargs
    )  # type: ignore

    # Fit the estimator_object for is_last==0 providing exogenous variables from estimator_config.
    current_estimator_object.fit(
        y=df.loc[df.is_last == 0, forecast_col_name].reset_index(drop=True),
        X=df.loc[df.is_last == 0, current_estimator.exogenous_vars].reset_index(
            drop=True
        ),
    )

    # Make the prediction for is_last==1.
    df.loc[df.is_last == 1, "pred"] = current_estimator_object.predict(
        X=df.loc[df.is_last == 1, current_estimator.exogenous_vars].reset_index(
            drop=True
        ),
    )

    return df
