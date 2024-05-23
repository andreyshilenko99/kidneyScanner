import atexit
import datetime
import json
import logging
import logging.config
import logging.handlers
import logging.handlers
import os
import pathlib
from logging.config import ConvertingList
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import Queue
from queue import Queue
from typing import Dict

import yaml

from settings import Config


def get_project_root() -> str:
    cur_file = os.path.abspath(__file__)
    while not os.path.exists(os.path.join(cur_file, 'settings.py')):
        cur_file = os.path.dirname(cur_file)
    return cur_file

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class MyJSONFormatter(logging.Formatter):
    def __init__(
            self,
            *,
            fmt_keys: Dict[str, str] or None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str, ensure_ascii=False)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": datetime.datetime.fromtimestamp(
                record.created, tz=datetime.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {}
        for key, val in self.fmt_keys.items():
            msg_val = always_fields.pop(val, None)
            message[key] = msg_val if msg_val is not None else getattr(record, val)

        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


class NonErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool or logging.LogRecord:
        return record.levelno <= logging.INFO


class Logger:
    _logger = None

    def __new__(cls, *args, **kwargs):
        config = Config()
        if cls._logger is None:
            root_path = get_project_root()
            print(root_path)
            config_file = pathlib.Path(config['LOG_CONFIG'])
            print(config_file)
            path_to_conf = os.path.join(root_path, config_file)
            print(path_to_conf)
            with open(path_to_conf) as ymlfile:
                config = yaml.safe_load(ymlfile)
            logging.config.dictConfig(config)
            cls._logger = logging.getLogger('root')

        return cls._logger


def _resolve_handlers(l):
    if not isinstance(l, ConvertingList):
        return l

    return [l[i] for i in range(len(l))]

# TODO Do we need this shit?
# def _resolve_queue(q):
#     if not isinstance(q, ConvertingDict):
#         return q
#     if '__resolved_value__' in q:
#         return q['__resolved_value__']
#
#     cname = q.pop('class')
#     klass = q.configurator.resolve(cname)
#     props = q.pop('.', None)
#     kwargs = {k: q[k] for k in q if valid_ident(k)}
#     result = klass(**kwargs)
#     if props:
#         for name, value in props.items():
#             setattr(result, name, value)
#
#     q['__resolved_value__'] = result
#     return result


class QueueListenerHandler(QueueHandler):

    def __init__(self, handlers, respect_handler_level=False, auto_run=True):
        # TODO get queue options from config
        self.queue = Queue(maxsize=1000)

        super().__init__(self.queue)
        handlers = _resolve_handlers(handlers)

        self._listener = QueueListener(
            self.queue,
            *handlers,
            respect_handler_level=respect_handler_level)
        if auto_run:
            self.start()
            atexit.register(self.stop)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def emit(self, record):
        return super().emit(record)
