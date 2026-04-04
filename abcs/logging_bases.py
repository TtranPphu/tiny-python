from abc import ABC, abstractmethod
from logging import Logger, Handler, getLogger as get_logger

from utils import path_str, fss


class HasLogger:
    def __init__(self, **kwargs):

        self._setup()

        super().__init__(**kwargs)

    def _setup(self):
        logger = self._get_logger()

        for handler in self._log_handlers():
            logger.addHandler(handler)

    def _get_logger(self) -> Logger:
        return get_logger(self._logger_name())

    def _logger_name(self) -> str:
        """Override this method to use custom logger name."""
        return self.__default_logger_name()

    def __default_logger_name(self) -> str:
        return self.__class__.__name__

    def _log_file_path(self) -> path_str:
        pass

    def _log_path(self) -> path_str:
        """Override this method to use custom log path."""
        return fss.abs(fss.cwd())

    def _log_handlers(self) -> list[Handler]:
        """Override this method to use custom log handlers."""
        return [self.__default_steam_handler(), self.__default_file_handler()]

    def __default_steam_handler(self) -> Handler:
        from logging import StreamHandler, Formatter, LogRecord

        class DefaultSteamFormatter(Formatter):
            def format(self, record: LogRecord):
                return f"{record.asctime} - {record.name} - {record.levelname} - {record.message}"

        steam_handler = StreamHandler()
        steam_handler.setFormatter(
            DefaultSteamFormatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

        return steam_handler

    def __default_file_handler(self) -> Handler:
        from logging import Formatter, LogRecord
        from logging.handlers import TimedRotatingFileHandler

        class DefaultFileFormatter(Formatter):
            def format(self, record: LogRecord):
                return f"{record.asctime} - {record.name} - {record.levelname} - {record.message}"

        file_handler = TimedRotatingFileHandler()
        return TimedRotatingFileHandler(f"{self.__default_logger_name()}.log")


class WillLogAttrChanges:
    def __setattr__(self, name, value):
        pass
