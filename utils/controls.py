from functools import wraps
from typing import Callable, TypeVar

R = TypeVar("R")


class controls:
    @staticmethod
    def run_once(func: Callable[..., R]) -> Callable[..., R]:
        class had_not_run:
            pass

        @wraps(func)
        def wrapper(*args, **kwargs) -> R:
            results = getattr(wrapper, "results", {})
            key = (args, frozenset(kwargs.items()))
            result = results.get(key, had_not_run())
            if isinstance(result, had_not_run):
                result = func(*args, **kwargs)
                results[key] = result
            return result

        return wrapper
