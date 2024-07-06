from tpa_analytics_engine.data_handler.prepare_forecast_format import add_columns
from tpa_analytics_engine.data_handler.prepare_forecast_format import (
    filter_n_days_before,
)


def test_add_columns(provide_data_frame):
    df = provide_data_frame

    new_col_set = {
        "day_of_week",
        "hour",
        "hour_format",
        "Day",
        "trend",
        "avg_daily_price_lag1",
        "avg_daily_price_lag2",
        "avg_daily_price_lag3",
        "is_last",
    }
    columns_df = set(df.columns)
    df_added = add_columns(df)
    assert len(columns_df.intersection(new_col_set)) == 0

    assert len(set(df_added.columns).intersection(new_col_set)) == len(new_col_set)


def test_filter_n_days_before(provide_data_frame, provide_data_config):
    df = provide_data_frame
    df_filtered = filter_n_days_before(df, 5)

    assert len(df[provide_data_config.date_column].dt.date.unique()) == 10
    assert len(df_filtered[provide_data_config.date_column].dt.date.unique()) == 5
