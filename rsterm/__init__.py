import dotenv
import os
import psycopg2
from psycopg2.extensions import connection
from configparser import ConfigParser
from typing import Dict
from pathlib import Path
from abc import ABC, abstractmethod
from argparse import Namespace, ArgumentParser


def parse_ini_config(ini_file_name: str, config_path: Path = None) -> ConfigParser:
    ini_config_path: Path = config_path or Path.cwd().absolute() / ini_file_name

    if ini_config_path.exists():
        config = ConfigParser()
        config.read(parse_ini_config)
        return config


def parse_terminal_args(args_config: Dict) -> Namespace:
    arg_parser = ArgumentParser()

    for command, options in args_config.items():
        arg_parser.add_argument(*command, **options)
    return arg_parser.parse_args()


def env_path_valid(env_file_path: Path) -> bool:
    if not env_file_path.exists():
        raise FileNotFoundError(f"no .env file found at {env_file_path.as_posix()}")
    return True


def load_app_env(file_name: str = ''):
    env_file_path = Path.cwd().absolute()
    if file_name:
        env_file_path = env_file_path / file_name
    else:
        env_file_path = env_file_path / '.env'

    if env_path_valid(env_file_path):
        dotenv.load_dotenv(env_file_path)


def get_db_connection(connection_name: str) -> psycopg2.connect:
    db_connection_string = os.getenv(connection_name)

    if db_connection_string:
        return psycopg2.connect(db_connection_string)
    else:
        raise EnvironmentError(f"no connection string found in .env for {connection_name}")


class EntryPoint(ABC):

    def __init__(self, args_config: Dict, ini_file_name: str = '.app_config'):
        self.cmd_args: Namespace = parse_terminal_args(args_config)
        self.config: ConfigParser = parse_ini_config(ini_file_name) or {}
        self.db_connection: connection = None

        try:
            self.env_file_name = self.config['app_env']['file_name']
        except KeyError:
            self.env_file_name = self.cmd_args.env_file

        try:
            self.env_var_name = self.config['environment']['env_var_name']
        except KeyError:
            self.env_var_name = self.cmd_args.env_var

        load_app_env(Path.cwd() / self.env_file_name)

    @abstractmethod
    def call(self) -> None:
        pass

    def set_db_connection(self):
        self.db_connection = get_db_connection(self.env_var_name)
