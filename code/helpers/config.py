from __future__ import annotations
from tomllib import load
from typing import Optional, Any

class Config:
    shared: Optional[Config] = None

    def __init__(self, config_path: str) -> None:
        with open(config_path, 'rb') as config_file:
            self.__dict = load(config_file)

    def __getitem__(self, key: str) -> Any:
        return self.__dict[key]

    @staticmethod
    def initialize(config_path: str) -> None:
        if Config.shared is not None:
            return
        Config.shared = Config(config_path)
