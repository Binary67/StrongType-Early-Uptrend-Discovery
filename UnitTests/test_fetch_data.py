import os
import pandas as pd
from scripts.fetch_data import DailyOhlcvLoader, FeatureMatrixBuilder


def CreateSampleCsv(path: str) -> pd.DataFrame:
    df = pd.DataFrame({
        "Open": [1.0, 2.0, 3.0],
        "High": [1.5, 2.5, 3.5],
        "Low": [0.5, 1.5, 2.5],
        "Close": [1.2, 2.2, 3.2],
        "Volume": [100, 200, 300]
    }, index=pd.date_range("2023-01-01", periods=3, freq="1d"))
    df.index.freq = None
    df.to_csv(path)
    return df


def test_loader_csv():
    csv_path = os.path.join("data", "sample.csv")
    df_original = CreateSampleCsv(csv_path)
    loader = DailyOhlcvLoader(source="csv")
    df = loader.load("SAMP", "2023-01-01", "2023-01-03", csv_path=csv_path)
    pd.testing.assert_frame_equal(df, df_original)


def DoubleClose(df: pd.DataFrame) -> pd.Series:
    return df["Close"] * 2


def test_feature_builder():
    csv_path = os.path.join("data", "sample.csv")
    df_original = CreateSampleCsv(csv_path)
    builder = FeatureMatrixBuilder([DoubleClose])
    features = builder.build(df_original)
    assert "DoubleClose" in features.columns
    pd.testing.assert_series_equal(features["DoubleClose"], df_original["Close"] * 2, check_names=False)
