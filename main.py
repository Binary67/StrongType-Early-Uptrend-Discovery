from genetic_uptrend_discovery.data.downloader import YFinanceDownloader
from genetic_uptrend_discovery.data.labeler import DataLabel


def main():
    """Demonstrate downloader and labeler usage."""
    downloader = YFinanceDownloader('AAPL', '2023-01-01', '2023-01-10', '1d')
    data = downloader.DownloadData()
    labeler = DataLabel(data)
    labeled = labeler.LabelUptrend()
    print(labeled.head())


if __name__ == '__main__':
    main()
