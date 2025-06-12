import os
import unittest
import pandas as pd
from scripts.fetch_data import DailyOHLCVLoader, FeatureMatrixBuilder


class TestDailyOHLCVLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.SamplePath = os.path.join(os.path.dirname(__file__), "sample.csv")
        Data = pd.DataFrame({
            "Open": [1, 2, 3, 4, 5],
            "High": [1.1, 2.1, 3.1, 4.1, 5.1],
            "Low": [0.9, 1.9, 2.9, 3.9, 4.9],
            "Close": [1, 2, 3, 4, 5],
            "Adj Close": [1, 2, 3, 4, 5],
            "Volume": [100, 200, 300, 400, 500]
        }, index=pd.date_range("2020-01-01", periods=5, freq="D"))
        Data.to_csv(self.SamplePath)

    def tearDown(self) -> None:
        if os.path.exists(self.SamplePath):
            os.remove(self.SamplePath)

    def test_csv_loader(self) -> None:
        Loader = DailyOHLCVLoader(Source="csv", CsvPath=self.SamplePath)
        DataFrame = Loader.Load()
        self.assertFalse(DataFrame.isnull().any().any())
        self.assertIn("Close", DataFrame.columns)

    def test_missing_bars(self) -> None:
        MissingPath = os.path.join(os.path.dirname(__file__), "missing.csv")
        Data = pd.DataFrame({
            "Open": [1, 3],
            "High": [1, 3],
            "Low": [1, 3],
            "Close": [1, 3],
            "Volume": [100, 300]
        }, index=[pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-03")])
        Data.to_csv(MissingPath)
        Loader = DailyOHLCVLoader(Source="csv", CsvPath=MissingPath)
        with self.assertRaises(ValueError):
            Loader.Load()
        os.remove(MissingPath)


class TestFeatureMatrixBuilder(unittest.TestCase):
    def test_build_matrix(self) -> None:
        Index = pd.date_range("2020-01-01", periods=60, freq="D")
        Data = pd.DataFrame({
            "Open": range(1, 61),
            "High": range(1, 61),
            "Low": range(1, 61),
            "Close": range(1, 61),
            "Volume": [100] * 60
        }, index=Index)
        Builder = FeatureMatrixBuilder(Data)
        Matrix = Builder.Build()
        for Column in ["Ema12", "Ema50", "Rsi14", "Atr14"]:
            self.assertIn(Column, Matrix.columns)
        self.assertGreater(len(Matrix), 0)


if __name__ == "__main__":
    unittest.main()
