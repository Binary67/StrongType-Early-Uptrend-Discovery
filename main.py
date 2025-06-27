from LoggerSetup import LoggerSetup
import logging


def main() -> None:
    LogSetup = LoggerSetup()
    LogFile = LogSetup.InitializeLogger()
    Logger = logging.getLogger(__name__)
    Logger.info("Application started; logging to %s", LogFile)


if __name__ == "__main__":
    main()
