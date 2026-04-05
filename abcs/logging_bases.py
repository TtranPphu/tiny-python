from abc import ABC, abstractmethod
from logging import Logger, Handler, getLogger as get_logger

from utils import path_str, fss, fsm


class HasLogger:
    logger: Logger

    def __init__(self, **kwargs):

        self.__setup()

        super().__init__(**kwargs)

    def __setup(self):
        fsm.ensure_dir_exists(self._log_folder())

        logger = get_logger(self._logger_name())

        for handler in self._log_handlers():
            logger.addHandler(handler)

        self.logger = logger

    def _logger_name(self) -> str:
        """Override this method to use custom logger name."""
        return self.__class__.__name__

    def _log_file(self) -> path_str:
        """Override this method to use custom log file."""
        return fss.join(self._log_folder(), self._logger_name(), extention="log")

    def _log_folder(self) -> path_str:
        """Override this method to use custom log folder."""
        return fss.join(fss.abs(fss.cwd()), ".logs")

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

        file_handler = TimedRotatingFileHandler(
            self._log_file(),
            when="midnight",
            backupCount=7,
            encoding="utf-8",
        )

        file_handler.setFormatter(
            DefaultFileFormatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

        return file_handler


class WillLogAttrChanges:
    def __setattr__(self, name, value):
        pass
