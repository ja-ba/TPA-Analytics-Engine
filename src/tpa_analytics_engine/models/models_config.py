from typing import Any
from typing import Dict
from typing import List

from pydantic import BaseModel
from pydantic import field_validator
from sklearn.ensemble import HistGradientBoostingRegressor


# Create the estimator_dict mapping all allowed models
estimator_dict: Dict[str, Dict[str, Any]] = {
    "sklearn": {"HistGradientBoostingRegressor": HistGradientBoostingRegressor}
}

# Pydantic Base Class for ForecEstimatorast
class Estimator_Config(BaseModel):
    """A pydantic class to specify the estimator configuration.
    The configuration specifies which estimator to use, potential keyword arguments and exogenous variables to use in the estimator.
    """

    estimator_type: Any
    estimator_kwargs: dict
    exogenous_vars: List[str]


# Pydantic Base Class for Forecast
class Forecast_Config(BaseModel):
    """A pydantic class to specify the forecast configuration.
    The configuration specifies:
        - n_before: the number of days to include for estimating the forecast model.
        - use_estimator_class: The estimator class to use --> the key of estimator_dict.
        - use_estimator: The estimator name to use --> must be a key in the sub-dictionary of use_estimator_class in estimator_dict.
        - estimators: A dictionary with the specified estimators and their configurations (Estimator_Configs).

    """

    n_before: int
    use_estimator_class: str
    use_estimator: str
    estimators: Dict[str, Dict[str, Estimator_Config]]

    @field_validator("use_estimator_class")
    def validate_use_estimator_class(cls, value):
        if value not in estimator_dict:
            raise ValueError(
                f"Invalid estimator_class in use_estimator_class. Allowed values are {estimator_dict.keys()}"
            )
        return value


def create_forecast_config(config_dict: dict) -> Forecast_Config:
    """A function taking in the config dict and extracting the Forecast_Config.

    Args:
        config_dict (dict): A dictionary containing the config with a key 'forecast_config'.

    Returns:
        Forecast_Config: A forecast configuration.
    """
    return Forecast_Config(**config_dict.get("forecast_config", {}))
