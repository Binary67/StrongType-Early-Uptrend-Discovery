from scripts.fetch_data import DailyOhlcvLoader, FeatureMatrixBuilder


def main() -> None:
    loader = DailyOhlcvLoader()
    df = loader.load("AAPL", "2023-01-01", "2023-02-01")
    builder = FeatureMatrixBuilder()
    features = builder.build(df)
    print(features.head())


if __name__ == "__main__":
    main()
