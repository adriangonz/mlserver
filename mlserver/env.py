import os
import sys

from typing import List

from .logging import logger


class Environment:
    """
    Custom Python environment.
    The class can be used as a context manager to enable / disable the custom
    environment.
    """

    def __init__(self, env_path: str, version_info: tuple) -> "Environment":
        if len(version_info) < 2:
            logger.warning(
                "Invalid version info. Expected, at least, two dimensions "
                f"(i.e. (major, minor, ...)) but got {version_info}"
            )

        self._env_path = env_path
        self._version_info = version_info

    @classmethod
    def from_executable(cls, executable: str, version_info: tuple) -> "Environment":
        """
        Alternative constructor to instantiate an environment from the Python
        bin executable (rather than the env path).
        """
        env_path = os.path.dirname(os.path.dirname(executable))
        return cls(env_path, version_info)

    @property
    def sys_path(self) -> List[str]:
        if len(self._version_info) < 2:
            return []

        major = self._version_info[0]
        minor = self._version_info[1]
        lib_path = os.path.join(self._env_path, "lib", f"python{major}.{minor}")

        return [
            f"{lib_path}.zip",
            lib_path,
            os.path.join(lib_path, "lib-dynload"),
            os.path.join(lib_path, "site-packages"),
        ]

    @property
    def bin_path(self) -> str:
        return os.path.join(self._env_path, "bin")

    def __enter__(self):
        self._prev_sys_path = sys.path
        self._prev_bin_path = os.environ["PATH"]

        sys.path = [*self.sys_path, *self._prev_sys_path]
        os.environ["PATH"] = os.pathsep.join([self.bin_path, self._prev_bin_path])

        return self

    def __exit__(self, *exc_details) -> None:
        sys.path = self._prev_sys_path
        os.environ["PATH"] = self._prev_bin_path
