import logging
from typing import Tuple

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
from sklearn.model_selection import train_test_split


class DataPreprocessor:
    """Utility class for preprocessing OHLCV time series."""

    def ResampleTimeSeries(self, PriceDf: pd.DataFrame, TargetInterval: str) -> pd.DataFrame:
        """Resample arbitrary bar intervals to the target frequency.

        Args:
            PriceDf: Data indexed by timestamps.
            TargetInterval: Pandas offset alias, e.g. '1D' or '1H'.

        Returns:
            pd.DataFrame: Resampled data aligned to the trading calendar.
        """
        PriceDf = PriceDf.sort_index()
        Aggregations = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        }
        ResampledDf = PriceDf.resample(TargetInterval).agg(Aggregations)
        CustomDay = CustomBusinessDay(calendar=USFederalHolidayCalendar())
        TradingDays = pd.date_range(
            start=ResampledDf.index.min(),
            end=ResampledDf.index.max(),
            freq=CustomDay,
        )
        ResampledDf = ResampledDf.reindex(TradingDays)
        ResampledDf["Volume"] = ResampledDf["Volume"].ffill()
        ResampledDf.ffill(inplace=True)
        return ResampledDf

    def HandleMissingValues(self, PriceDf: pd.DataFrame, Strategy: str) -> pd.DataFrame:
        """Impute missing values according to the specified strategy."""
        if Strategy == "ffill":
            CleanDf = PriceDf.ffill()
        elif Strategy == "bfill":
            CleanDf = PriceDf.bfill()
        elif Strategy == "interpolate":
            CleanDf = PriceDf.interpolate()
        elif Strategy == "drop":
            CleanDf = PriceDf.dropna()
        else:
            raise ValueError(f"Unknown Strategy: {Strategy}")
        return CleanDf

    def SplitTrainTestSets(
        self,
        PriceDf: pd.DataFrame,
        TrainRatio: float,
        ValidationRatio: float,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split the data into chronological train, validation and test sets."""
        PriceDf = PriceDf.sort_index()
        TrainDf, TempDf = train_test_split(
            PriceDf, train_size=TrainRatio, shuffle=False
        )
        ValSize = ValidationRatio / (1 - TrainRatio)
        ValidationDf, TestDf = train_test_split(
            TempDf, train_size=ValSize, shuffle=False
        )
        Logger = logging.getLogger(__name__)
        Logger.info(
            "Training data from %s to %s", TrainDf.index.min(), TrainDf.index.max()
        )
        Logger.info(
            "Validation data from %s to %s", ValidationDf.index.min(), ValidationDf.index.max()
        )
        Logger.info(
            "Hold-out data from %s to %s", TestDf.index.min(), TestDf.index.max()
        )
        return TrainDf, ValidationDf, TestDf
