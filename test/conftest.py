import pytest
from cloud_storage_wrapper.oci_access.config import create_OCI_Connection_from_dict
from cloud_storage_wrapper.oci_access.pandas import create_PandasOCI_from_dict
from tpa_analytics_engine.api import Forecast
from tpa_analytics_engine.data_handler.prepare_forecast_format import add_columns
from tpa_analytics_engine.data_handler.prepare_forecast_format import Data_Config
from tpa_analytics_engine.data_handler.prepare_forecast_format import load_station_sorte
from tpa_analytics_engine.models.models_config import create_forecast_config
from tpa_analytics_engine.utils import get_config

config_path = "test/test_config.yaml"


@pytest.fixture(scope="session")
def provide_config():
    return get_config(config_path)


@pytest.fixture(scope="session")
def provide_oci_config(provide_config):
    return create_OCI_Connection_from_dict(provide_config)


@pytest.fixture(scope="session")
def provide_oci_pandas_config(provide_config):
    return create_PandasOCI_from_dict(provide_config)


@pytest.fixture(scope="session")
def provide_data_config(provide_config, provide_oci_config):
    return Data_Config(**provide_config["data_config"])


@pytest.fixture(scope="session")
def provide_data_frame(provide_data_config, provide_oci_pandas_config):
    return load_station_sorte(
        pandas_connection=provide_oci_pandas_config,
        data_config=provide_data_config,
        sorte="diesel",
        station="9771",
        add_pred=False,
    )


@pytest.fixture(scope="session")
def provide_data_frame_transformed(provide_data_frame):
    return add_columns(provide_data_frame)


@pytest.fixture(scope="session")
def provide_forecast_config(provide_config):
    return create_forecast_config(provide_config)


@pytest.fixture(scope="function")
def provide_Forecast_object(provide_config):
    return Forecast(config_path=config_path)
