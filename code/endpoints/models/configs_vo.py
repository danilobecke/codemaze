from __future__ import annotations

class ConfigsVO:
    def __init__(self, create_test_script_url: str, language_configs: list[LanguageConfigVO]) -> None:
        self.create_test_script_url = create_test_script_url
        self.configs = language_configs

class LanguageConfigVO:
    def __init__(self, language_name: str, supported_extensions: list[str], _help: str) -> None:
        self.language_name = language_name
        self.supported_extensions = supported_extensions
        self._help = _help
