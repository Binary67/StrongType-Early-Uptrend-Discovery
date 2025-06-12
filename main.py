from scripts.fetch_data import DailyOhlcvLoader, FeatureMatrixBuilder


def main() -> None:
    loader = DailyOhlcvLoader()
    try:
        df = loader.load("AAPL", "2023-01-01", "2023-02-01")
    except ValueError as exc:
        print(f"Data loading failed: {exc}")
        return

    builder = FeatureMatrixBuilder()
    features = builder.build(df)
    print(features.head())


if __name__ == "__main__":
    main()
