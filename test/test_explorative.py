import pytest
from tpa_analytics_engine.explorative.summaries import mean_centralize
from tpa_analytics_engine.explorative.summaries import summarize

# from tpa_analytics_engine.explorative.summaries import extract_time


def test_summarize(provide_data_frame_transformed):
    test_df_summarized = summarize(
        provide_data_frame_transformed.query("is_last== 0"),
        groupCol="day_of_week",
        aggCol="price",
    )
    assert len(test_df_summarized) == 7
    assert (test_df_summarized > 0).sum() == 7
    assert (
        abs(
            test_df_summarized.mean()
            - provide_data_frame_transformed.query("is_last== 0")["price"].mean()
        )
        < 0.1
    )

    with pytest.raises(ValueError):
        summarize(
            provide_data_frame_transformed.is_last == 0, groupCol="foo", aggCol="price"
        )

    with pytest.raises(ValueError):
        summarize(
            provide_data_frame_transformed.is_last == 0,
            groupCol="day_of_week",
            aggCol="foo",
        )


def test_mean_centralize(provide_data_frame_transformed):
    test_df_summarized_centralized = mean_centralize(
        summarize(
            provide_data_frame_transformed.query("is_last== 0"),
            groupCol="day_of_week",
            aggCol="price",
        )
    )

    assert abs(test_df_summarized_centralized.mean()) < 0.1


# def test_extract_time(provide_data_frame_transformed, provide_data_config):
#     assert (
#         provide_data_frame_transformed[provide_data_config.date_column].dtype
#         == "timestamp[ns][pyarrow]"
#     )
#     assert (
#         extract_time(
#             provide_data_frame_transformed[provide_data_config.date_column]
#         ).dtype
#         == "time64[ns][pyarrow]"
#     )
