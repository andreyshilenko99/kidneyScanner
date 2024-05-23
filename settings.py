import argparse
import os

import yaml
from yaml import Loader


class Config:
    _config = None

    def __new__(cls, path: str = None, *args, **kwargs):
        if cls._config is None:
            cls._config = {}
            wd = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(wd, path)
            if os.path.exists(path) and os.path.isfile(path):
                with open(os.path.join(wd, os.path.join(wd, path)), 'r') as ymlfile:
                    cfg = yaml.load(ymlfile, Loader=Loader)
            else:
                return FileNotFoundError
            if cfg:
                for key in cfg:
                    if key in cfg:
                        cls._config[key] = cfg[key]
                    else:
                        cls._config.update({key: cfg[key]})
                if os.path.exists(os.path.join(wd, cls._config['LOG_CONFIG'])):
                    pass
                else:
                    cls._config['LOG_CONFIG'] = os.path.join(wd, 'config/config_logs.default.yaml')
                return cls._config

        else:
            return cls._config


def get_args():
    parser = argparse.ArgumentParser(description='ARGS')

    parser.add_argument('--config', dest='config', default='./config', required=False, type=str,
                        help='Path to config file.')

    return parser.parse_args()



