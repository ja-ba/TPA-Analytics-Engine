from unittest.mock import patch

import pytest
from pydantic import ValidationError
from tpa_analytics_engine.models.make_forecast import run
from tpa_analytics_engine.models.models_config import create_forecast_config
from tpa_analytics_engine.models.sklearn import forecast_sklearn


def test_create_forecast_config(provide_config):
    # Test that error is thrown for invalid use_estimator_class
    with patch.dict(
        provide_config["forecast_config"], {"use_estimator_class": "invalid"}
    ):
        with pytest.raises(ValueError):
            create_forecast_config(provide_config)

    # Test that error is thrown for missing field
    with patch.dict(provide_config["forecast_config"], {"n_before": {}}, clear=True):
        with pytest.raises(ValidationError):
            create_forecast_config(provide_config)

    # Test that error is thrown for invalid data type
    with patch.dict(provide_config["forecast_config"], {"n_before": "invalid"}):
        del provide_config["forecast_config"]["n_before"]
        with pytest.raises(ValidationError):
            create_forecast_config(provide_config)


def test_run(provide_forecast_config, provide_data_frame_transformed):
    forecast_df = run(
        df=provide_data_frame_transformed, forecast_config=provide_forecast_config
    )

    assert "pred" in forecast_df
    assert forecast_df.loc[forecast_df.is_last == 1, "pred"].mean() > 0
    assert forecast_df.loc[forecast_df.is_last == 0, "pred"].isna().sum() == len(
        forecast_df.query("is_last == 0")
    )


def test_forecast_sklearn(provide_forecast_config, provide_data_frame_transformed):
    forecast_df = forecast_sklearn(
        df=provide_data_frame_transformed, forecast_config=provide_forecast_config
    )

    assert "pred" in forecast_df
    assert forecast_df.loc[forecast_df.is_last == 1, "pred"].mean() > 0
    assert forecast_df.loc[forecast_df.is_last == 0, "pred"].isna().sum() == len(
        forecast_df.query("is_last == 0")
    )
