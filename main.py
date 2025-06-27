from ConfigManager import ConfigManager
from LoggerSetup import LoggerSetup
import logging


def main() -> None:
    LogSetup = LoggerSetup()
    LogFile = LogSetup.InitializeLogger()
    Config = ConfigManager()
    Parameters = Config.LoadConfig()
    Logger = logging.getLogger(__name__)
    Logger.info("Application started; logging to %s", LogFile)
    Logger.info("Loaded configuration: %s", Parameters)


if __name__ == "__main__":
    main()
