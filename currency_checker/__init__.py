from importlib import metadata
from typing import Final


APP_NAME: Final[str] = 'currency_checker'
try:
    __version__ = metadata.version(APP_NAME)
except metadata.PackageNotFoundError:
    __version__ = '0.1.0'
