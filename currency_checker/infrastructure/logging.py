import logging.config
from datetime import datetime, timezone
from logging import LogRecord
from pathlib import Path
from typing import Any, Dict, Optional, Union, cast

import yaml
from pythonjsonlogger import jsonlogger


LEVEL_TO_NAME: Dict[int, str] = {
    logging.CRITICAL: 'FATAL',
    logging.ERROR: 'ERROR',
    logging.WARNING: 'WARN',
    logging.INFO: 'INFO',
    logging.DEBUG: 'DEBUG',
    logging.NOTSET: 'TRACE',
}


class UvicornAccessLogFilter(logging.Filter):
    def __init__(self, path: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__path = path

    def filter(self, record: logging.LogRecord) -> bool:
        if not isinstance(record.args, tuple):
            return True
        try:
            path = cast(str, record.args[2])
            status_code = cast(int, record.args[4])
        except IndexError:
            return True
        return (
            not isinstance(path, str) or
            not isinstance(status_code, int) or
            status_code >= 400 or
            not path.startswith(self.__path)
        )


class JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: Dict, record: LogRecord, message_dict: Dict) -> None:
        super().add_fields(log_record, record, message_dict)

        log_record['_time'] = datetime.now(timezone.utc).isoformat()
        log_record['_thread'] = f'{record.thread}:{record.threadName}'
        log_record['_level'] = LEVEL_TO_NAME.get(record.levelno, 'ERROR')

        log_record['_context'] = log_record.pop('name', None)
        if not log_record['_context']:
            log_record['_context'] = record.name

        log_record['_message'] = log_record.pop('message', None)
        if not log_record['_message']:
            log_record['_message'] = getattr(record, 'message', record.msg)


def configure_logging(path_to_log_config: Optional[Path] = None, root_level: Union[str, int, None] = None) -> None:
    if not path_to_log_config:
        logging.basicConfig(level=root_level or logging.DEBUG)
        return
    with open(path_to_log_config, 'r') as file:
        loaded_config = yaml.safe_load(file)
    logging.config.dictConfig(loaded_config)
    if root_level:
        logging.root.setLevel(root_level)
