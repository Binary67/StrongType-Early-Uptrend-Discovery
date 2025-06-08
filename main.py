from genetic_uptrend_discovery.data.downloader import YFinanceDownloader
from genetic_uptrend_discovery.data.labeler import DataLabel
from genetic_uptrend_discovery.src.indicators.technical import (
    CalculateEma,
    CalculateRsi,
    CalculateMacd,
)


def main():
    """Demonstrate downloader and labeler usage."""
    downloader = YFinanceDownloader('AAPL', '2023-01-01', '2023-01-10', '1d')
    data = downloader.DownloadData()
    labeler = DataLabel(data)
    labeled = labeler.LabelUptrend()
    labeled['Ema12'] = CalculateEma(labeled['Close'], 12)
    labeled['Rsi14'] = CalculateRsi(labeled['Close'])
    macd_df = CalculateMacd(labeled['Close'])
    labeled = labeled.join(macd_df)
    print(labeled[['Ema12', 'Rsi14', 'Macd', 'Signal', 'Histogram']].head())


if __name__ == '__main__':
    main()
