import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from DataPreprocessor import DataPreprocessor


def test_resample_timeseries_preserves_volume():
    Index = pd.date_range("2020-01-02", "2020-01-03 23:00:00", freq="h")
    Data = pd.DataFrame(
        {
            "Open": 1,
            "High": 2,
            "Low": 0,
            "Close": 1,
            "Volume": 1,
        },
        index=Index,
    )
    Processor = DataPreprocessor()
    Resampled = Processor.ResampleTimeSeries(Data, "1D")
    # Weekend days should be excluded when aligning to trading calendar
    assert all(Day.weekday() < 5 for Day in Resampled.index)
    assert Resampled["Volume"].sum() == len(Index)


def test_handle_missing_values_ffill():
    Df = pd.DataFrame({"Close": [1.0, None, 3.0]})
    Processor = DataPreprocessor()
    Clean = Processor.HandleMissingValues(Df, "ffill")
    assert not Clean.isna().any().any()


def test_split_train_test_sets_order():
    Index = pd.date_range("2020-01-01", periods=10)
    Df = pd.DataFrame({"Close": range(10)}, index=Index)
    Processor = DataPreprocessor()
    Train, Validation, Test = Processor.SplitTrainTestSets(Df, 0.6, 0.2)
    assert len(Train) == 6
    assert len(Validation) == 2
    assert len(Test) == 2
    assert Train.index.max() < Validation.index.min()
    assert Validation.index.max() < Test.index.min()
