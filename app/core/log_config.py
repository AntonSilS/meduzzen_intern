import logging


class LoggingConfig:
    LOG_FILE_PATH = "myapp.log"
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    @staticmethod
    def configure_logging():

        logging.basicConfig(
            filename=LoggingConfig.LOG_FILE_PATH,
            level=LoggingConfig.LOG_LEVEL,
            format=LoggingConfig.LOG_FORMAT,
        )
