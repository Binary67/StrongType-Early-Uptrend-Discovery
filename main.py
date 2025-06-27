import logging
from ConfigManager import ConfigManager
from LoggerSetup import LoggerSetup
from DataDownloader import YFinanceDownloader
from DataLabel import DataLabel


def main() -> None:
    LogSetup = LoggerSetup()
    LogFile = LogSetup.InitializeLogger()
    Config = ConfigManager()
    Parameters = Config.LoadConfig()
    Logger = logging.getLogger(__name__)
    Logger.info("Application started; logging to %s", LogFile)
    Logger.info("Loaded configuration: %s", Parameters)

    Downloader = YFinanceDownloader(
        StartDate="2020-01-01",
        EndDate="2020-12-31",
        Interval="1d",
    )
    Data = Downloader.DownloadData()
    Logger.info(
        "Downloaded %d rows for ticker %s",
        len(Data),
        Downloader.Ticker,
    )

    Labeler = DataLabel(Data)
    LabeledData = Labeler.LabelUptrend()
    Logger.info("Labelled data with %d rows", len(LabeledData))


if __name__ == "__main__":
    main()
