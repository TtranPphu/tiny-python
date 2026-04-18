from ..utils import (
    file_system_manipulation as fsm,
    file_system_status as fss,
    path_str,
)

from logging import Logger, Handler, Formatter, getLogger as get_logger


class DefaultLogger(Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _log(self, *args, **kwargs):
        import traceback

        stack = traceback.extract_stack()
        stacklevel = kwargs.pop("stacklevel", 1)
        stacklevel += 1

        for frame in reversed(stack[:-2]):
            if frame.filename != __file__:
                break
            stacklevel += 1

        kwargs["stacklevel"] = stacklevel
        return super()._log(*args, **kwargs)


class HasLogger:
    logger: Logger

    def __init__(self, **kwargs):
        self.__setup()
        super().__init__(**kwargs)

    def __setup(self):
        fsm.ensure_dir_exists(self._log_folder())
        self.logger = self.__logger()
        __logger_class = self.logger.__class__.__name__
        __logger_name = self._logger_name()
        self.logger.debug(f"{__logger_class}({__logger_name}) initialized")

    def __logger(self) -> Logger:
        from logging import DEBUG

        logger = DefaultLogger(get_logger(self._logger_name()))
        if logger.hasHandlers():
            return logger

        logger.setLevel(DEBUG)

        for handler in self._log_handlers():
            logger.addHandler(handler)

        return logger

    def _logger_name(self) -> str:
        """Override this method to use custom logger name."""
        return self.__class__.__name__

    def _log_handlers(self) -> list[Handler]:
        """Override this method to use custom log handlers."""
        return [self.__default_steam_handler(), self.__default_file_handler()]

    def _log_folder(self) -> path_str:
        """Override this method to use custom log folder."""
        return fss.join(fss.abs(fss.cwd()), ".logs")

    def _log_file(self) -> path_str:
        """Override this method to use custom log file."""
        return fss.join(self._log_folder(), self._logger_name(), extention="log")

    class DefaultFormatter(Formatter):
        def format(self, record):
            from re import sub

            base = super().format(record)
            trimmed = sub(r" +", " ", base).replace("\n", " ")
            relative = fss.rel(record.pathname)
            return trimmed.replace(record.pathname, relative, 1)

    def __default_steam_handler(self) -> Handler:
        from logging import StreamHandler, DEBUG

        class DefaultSteamFormatter(self.DefaultFormatter):
            pass

        steam_handler = StreamHandler()
        steam_formatter = DefaultSteamFormatter(
            fmt="%(pathname)s:%(lineno)d | "
            f"{self.__class__.__name__} | %(funcName)s | "
            "[%(levelname)s] | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S %z",
        )
        steam_handler.setFormatter(steam_formatter)
        steam_handler.setLevel(DEBUG)

        return steam_handler

    def __default_file_handler(self) -> Handler:
        from logging import INFO
        from logging.handlers import TimedRotatingFileHandler

        class DefaultFileFormatter(self.DefaultFormatter):
            pass

        file_handler = TimedRotatingFileHandler(self._log_file(), when="midnight")
        file_formatter = DefaultFileFormatter(
            fmt="%(asctime)s | %(pathname)s:%(lineno)d | "
            f"{self.__class__.__name__} | %(funcName)s | "
            "[%(levelname)s] | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S %z",
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(INFO)

        return file_handler


class WillLogAttrChanges(HasLogger):
    from pandas import DataFrame

    _S: dict[type, type]
    _M: dict[type, type]
    _F: dict[type, type]

    @classmethod
    def wrap(cls, manager: "WillLogAttrChanges", variable: str, value):
        def __log(t):
            if hasattr(manager, "logger"):
                # manager.logger.debug(f"Wrapping {variable} as {t}")
                pass

        if (__t := type(value)) in cls._M:
            for k, v in value.items():
                value[k] = cls.wrap(manager, f"{variable}[{k}]", v)
            __log(cls._M[__t].__name__)
            return cls._M[__t](manager, variable, **value)
        elif (__t := type(value)) in cls._F:
            for c, v in value.items():
                value[c] = cls.wrap(manager, f"{variable}[{c}]", v)
            __log(cls._F[__t].__name__)
            return cls._F[__t](manager, variable, value)
        elif (__t := type(value)) in cls._S:
            for i, v in enumerate(value):
                value[i] = cls.wrap(manager, f"{variable}[{i}]", v)
            __log(cls._S[__t].__name__)
            return cls._S[__t](manager, variable, *value)
        return value

    class ObservableList(list):
        def __init__(self, manager: "WillLogAttrChanges", variable: str, *args):
            super().__init__(*args)
            self.__manager = manager
            self.__variable = variable

        def __setitem__(self, index, value):
            value = self.__manager.wrap(
                manager=self.__manager,
                variable=f"{self.__variable}[{index}]",
                value=value,
            )
            if hasattr(self.__manager, "logger"):
                self.__manager.logger.debug(f"{self.__variable}[{index}] = {value}")
            super().__setitem__(index, value)

        def append(self, value):
            value = self.__manager.wrap(
                manager=self.__manager,
                variable=f"{self.__variable}[{len(self)}]",
                value=value,
            )
            if hasattr(self.__manager, "logger"):
                self.__manager.logger.debug(f"{self.__variable}[{len(self)}] = {value}")
            super().append(value)

    class ObservableDict(dict):
        def __init__(self, manager: "WillLogAttrChanges", variable: str, **kwargs):
            super().__init__(**kwargs)
            self.__manager = manager
            self.__variable = variable

        def __setitem__(self, key, value):
            value = self.__manager.wrap(
                manager=self.__manager,
                variable=f"{self.__variable}[{key}]",
                value=value,
            )
            if hasattr(self.__manager, "logger"):
                self.__manager.logger.debug(f"{self.__variable}[{key}] = {value}")
            super().__setitem__(key, value)

    class ObservableDataFrame(DataFrame):
        class ObservableLocIndexer:
            pass

        class ObservableILocIndexer:
            pass

        def __init__(
            self, manager: "WillLogAttrChanges", variable: str, *args, **kwargs
        ):
            super().__init__(*args, **kwargs)
            self.__manager = manager
            self.__variable = variable

        def isetitem(self, loc, value):
            value = self.__manager.wrap(
                manager=self.__manager,
                variable=f"{self.__variable}[{loc}]",
                value=value,
            )
            if hasattr(self.__manager, "logger"):
                self.__manager.logger.debug(f"{self.__variable}[{loc}] = {value}")
            return super().isetitem(loc, value)

        def __setitem__(self, key, value):
            value = self.__manager.wrap(
                manager=self.__manager,
                variable=f"{self.__variable}[{key}]",
                value=value,
            )
            if hasattr(self.__manager, "logger"):
                self.__manager.logger.debug(f"{self.__variable}[{key}] = {value}")
            super().__setitem__(key, value)

        def rename(self, *args, **kwargs):
            if self.__manager.logger:
                message = "{v}.rename({p})"
                __v = self.__variable
                __a = list(args) + [f"{k}={v}" for k, v in kwargs.items()]
                __p = f"{', '.join(__a)}"
                self.__manager.logger.debug(message.format(v=__v, p=__p))
            return super().rename(*args, **kwargs)

        def drop(self, *args, **kwargs):
            if self.__manager.logger:
                __v = self.__variable
                __a = list(args) + [f"{k}={v}" for k, v in kwargs.items()]
                __p = f"{', '.join(__a)}"
                message = "{v}.drop({p})"
                self.__manager.logger.debug(message.format(v=__v, p=__p))
            return super().drop(*args, **kwargs)

    _S = {list: ObservableList}
    _M = {dict: ObservableDict}
    _F = {DataFrame: ObservableDataFrame}

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            if key.startswith("_"):
                continue
            kwargs[key] = self.wrap(
                manager=self,
                variable=key,
                value=value,
            )
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        value = self.wrap(
            manager=self,
            variable=name,
            value=value,
        )
        if hasattr(self, "logger"):
            self.logger.debug(f"{name} = {value}")
        super().__setattr__(name, value)
