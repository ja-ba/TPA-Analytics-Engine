import pytest


def test_load_df(provide_Forecast_object):
    provide_Forecast_object.load_df(sorte="diesel", station="9771")

    assert len(provide_Forecast_object.df) > 0


def test_create_forecast(provide_Forecast_object):
    with pytest.raises(ValueError):
        provide_Forecast_object.create_forecast()

    provide_Forecast_object.load_df(sorte="diesel", station="9771")
    forecast_df = provide_Forecast_object.create_forecast()

    assert "pred" in forecast_df
    assert forecast_df.loc[forecast_df.is_last == 1, "pred"].mean() > 0
    assert forecast_df.loc[forecast_df.is_last == 0, "pred"].isna().sum() == len(
        forecast_df.query("is_last == 0")
    )


def test_create_summaries(provide_Forecast_object):
    with pytest.raises(ValueError):
        provide_Forecast_object.create_summaries(
            groupCol="day_of_week", centralize_mean=True
        )

    provide_Forecast_object.load_df(sorte="diesel", station="9771")

    with pytest.raises(ValueError):
        provide_Forecast_object.create_summaries(
            groupCol="invalid_col", centralize_mean=True
        )

    summary_day = provide_Forecast_object.create_summaries(
        groupCol="day_of_week", centralize_mean=True
    )
    summary_hour = provide_Forecast_object.create_summaries(
        groupCol="hour", centralize_mean=True
    )
    summary_week = provide_Forecast_object.create_summaries(
        groupCol="week", centralize_mean=False
    )

    assert len(summary_day) >= 5
    assert len(summary_day) == len(provide_Forecast_object.df["day_of_week"].unique())
    assert abs(summary_day.mean()) < 1
    assert len(summary_hour) >= 12
    assert len(summary_hour) == len(provide_Forecast_object.df["hour"].unique())
    assert abs(summary_hour.mean()) < 1
    assert len(summary_week) == len(provide_Forecast_object.df["week"].unique())
    assert summary_week.mean() > 1
