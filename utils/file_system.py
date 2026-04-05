import os
import shutil
from .prelude import path_str


class file_system_status:
    @staticmethod
    def cwd() -> path_str:
        return file_system_status.std(os.getcwd())

    @staticmethod
    def abs(path: path_str) -> path_str:
        return file_system_status.std(os.path.abspath(path))

    @staticmethod
    def exists(path: path_str) -> bool:
        return os.path.exists(path)

    @staticmethod
    def is_file(path: path_str) -> bool:
        return os.path.isfile(path)

    @staticmethod
    def is_dir(path: path_str) -> bool:
        return os.path.isdir(path)

    @staticmethod
    def join(*components: path_str | str, extention: str = "") -> path_str:
        return file_system_status.std(f"{'/'.join(components)}.{extention}")

    @staticmethod
    def split(path: path_str) -> list[str]:
        return path.split("/")

    @staticmethod
    def std(path: path_str) -> path_str:
        from re import sub

        r = sub(r"/+", r"/", path)
        return r if r[-1] != "/" else r[:-1]


class file_system_manipulation:
    @staticmethod
    def ensure_dir_exists(path: path_str):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def ensure_file_exists(path: path_str):
        with open(path, "w") as _:
            pass

    @staticmethod
    def remove(path: path_str):
        if not file_system_status.exists(path):
            return
        if file_system_status.is_file(path):
            os.remove(path)
        elif file_system_status.is_dir(path):
            shutil.rmtree(path)

    @staticmethod
    def copy(src: path_str, dst: path_str):
        if file_system_status.is_file(src):
            shutil.copy2(src, dst)
        elif file_system_status.is_dir(src):
            shutil.copytree(src, dst)

    @staticmethod
    def move(src: path_str, dst: path_str):
        shutil.move(src, dst)

    @staticmethod
    def change_permission(path: path_str, mode: int):
        os.chmod(path, mode)
