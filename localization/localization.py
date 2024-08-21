import inspect
import pathlib

import yaml


def load_localization(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


class Localization:
    def __init__(self, locale: str):
        self.locale = locale
        self.translations = load_localization(f"{pathlib.Path(__file__).parent.resolve()}/locales/{locale}.yaml")

    def get(self, key: str) -> str:
        core_path = inspect.stack()[1].filename

        filename = "bot"

        if "\\" in core_path:
            filename = core_path.split("\\")[-2]
        elif "/" in core_path:
            filename = core_path.split("/")[-2]

        keys = [filename, key]
        value = self.translations

        for k in keys:
            value = value.get(k)
            if value is None:
                return key

        return value
