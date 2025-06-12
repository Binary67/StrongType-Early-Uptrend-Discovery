import argparse
import os
from scripts.fetch_data import DailyOHLCVLoader, FeatureMatrixBuilder


def Main() -> None:
    Parser = argparse.ArgumentParser(description="Data loading and feature build demo")
    Parser.add_argument("--source", default="yfinance", choices=["yfinance", "csv"], help="Data source")
    Parser.add_argument("--ticker", default="AAPL", help="Ticker symbol for yfinance")
    Parser.add_argument("--start", default="2020-01-01", help="Start date YYYY-MM-DD")
    Parser.add_argument("--end", default="2020-12-31", help="End date YYYY-MM-DD")
    Parser.add_argument("--csv-path", default=None, help="CSV path if using csv source")
    Arguments = Parser.parse_args()

    Loader = DailyOHLCVLoader(Source=Arguments.source, Ticker=Arguments.ticker,
                               CsvPath=Arguments.csv_path, StartDate=Arguments.start,
                               EndDate=Arguments.end)
    DataFrame = Loader.Load()
    Builder = FeatureMatrixBuilder(DataFrame)
    Features = Builder.Build()
    os.makedirs("data", exist_ok=True)
    Features.to_csv(os.path.join("data", f"{Arguments.ticker}_features.csv"))
    print(Features.head())


if __name__ == "__main__":
    Main()
