from __future__ import annotations
from tomllib import load
from typing import Optional, Any

from helpers.unwrapper import unwrap

# https://github.com/pylint-dev/pylint/issues/8987
# pylint: disable=protected-access,unused-private-member
class Config:
    __shared: Optional[Config] = None

    def __init__(self, config_path: str) -> None:
        with open(config_path, 'rb') as config_file:
            self.__dict = load(config_file)

    @staticmethod
    def get(key_path: str) -> Any:
        keys = key_path.split('.')
        keys_size = len(keys)
        current_dict = unwrap(Config.__shared).__dict.copy()
        value: Any | None = None
        for position, key in enumerate(keys):
            if position == keys_size - 1:
                value = current_dict[key] # last element
                break
            current_dict = dict[str, Any](current_dict[key])
        return unwrap(value)

    @staticmethod
    def initialize(config_path: str) -> None:
        if Config.__shared is not None:
            return
        Config.__shared = Config(config_path)
