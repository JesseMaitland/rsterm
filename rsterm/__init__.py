import dotenv
import os
import psycopg2
import pkgutil
import inspect
import yaml
from typing import List, NamedTuple, Tuple, Any, Dict
from importlib import import_module
from psycopg2.extensions import connection
from pathlib import Path
from abc import ABC, abstractmethod
from argparse import Namespace, ArgumentParser


DEFAULT_CONFIG_PATH = Path().cwd() / 'rsterm.yml'
DEFAULT_ENV_FILE = Path().cwd() / '.env'
DEFAULT_DB_CONNECTION_NAME = 'redshift'


class AWSSecrets(NamedTuple):
    key: str
    secret: str


class TerminalArgs:

    def __init__(self, verbs: List[str], nouns: List[str]) -> None:
        self._args = {
            'verbs': verbs,
            'nouns': nouns
        }

        self._formatted_args = {

            ('verb', ): {
                'help': 'The action you would like to perform',
                'choices': verbs
            },

            ('noun', ): {
                'help': 'The element to act upon',
                'choices': nouns
            }
        }

    @property
    def nouns(self) -> List[str]:
        return self._args['nouns']

    @property
    def verbs(self) -> List[str]:
        return self._args['verbs']

    @property
    def formatted_args(self) -> Dict[Tuple[str], Dict[str, Any]]:
        return self._formatted_args

    def add_nouns(self, *args: List[str]) -> None:
        nouns = self._args['nouns']
        noun_set = list(set(nouns.extend(args)))
        self._args['nouns'] = noun_set

    def add_verbs(self, *args: List[str]) -> None:
        verbs = self._args['verbs']
        verb_set = list(set(verbs.extend(args)))
        self._args['verbs'] = verb_set

    def add_args(self, args: Dict[Tuple[str], Dict[str, Any]]):
        self._formatted_args.update(args)


class RSTermConfig:

    def __init__(self, **kwargs):
        self._config = kwargs

    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        self._config[key] = value

    def get_terminal_args(self):
        terminal_args = self._config['rsterm']['terminal']
        return TerminalArgs(verbs=terminal_args['verbs'], nouns=terminal_args['nouns'])

    def get_db_connection_string(self, connection_name: str) -> str:
        return self._config['rsterm']['db_connections'][connection_name]

    def get_aws_secrets(self) -> AWSSecrets:
        return AWSSecrets(**self._config['rsterm']['aws_secrets'])

    def get_iam_role(self, role_name: str) -> str:
        return self._config['iam_roles'][role_name]

    def get_s3_bucket(self, bucket_name: str) -> str:
        return self._config['s3_buckets'][bucket_name]

    def get_env_file_name(self, env_name: str) -> str:
        return self._config['environment'][env_name]


def parse_config(config_path: Path = None) -> RSTermConfig:
    config_path: Path = config_path or Path.cwd().absolute() / 'rsterm.yml'

    if config_path.exists():
        config = yaml.safe_load(config_path.open())
        return RSTermConfig(**config)


def parse_terminal_args(args_config: Dict) -> Namespace:
    arg_parser = ArgumentParser()

    for command, options in args_config.items():
        arg_parser.add_argument(*command, **options)
    return arg_parser.parse_args()


def load_app_env(env_file_path: Path):

    if not env_file_path.exists():
        raise FileNotFoundError(f"no .env file found at {env_file_path.as_posix()}")
    else:
        dotenv.load_dotenv(env_file_path)


def get_db_connection(connection_name: str) -> psycopg2.connect:
    db_connection_string = os.getenv(connection_name)

    if db_connection_string:
        return psycopg2.connect(db_connection_string)
    else:
        raise EnvironmentError(f"no connection string found in .env for {connection_name}")


def import_entry_points():
    modules = []
    ep_path = Path() / "entrypoints"

    for _, name, _ in pkgutil.iter_modules([ep_path]):
        module = import_module(f"{ep_path.as_posix()}.{name}")
        modules.append(module)

    modules.append(import_module(ep_path.as_posix()))

    for m in modules:
        for name, obj in inspect.getmembers(m):
            if inspect.isclass(obj):
                if obj.__name__ != 'EntryPoint':
                    obj({}).call()




class EntryPoint(ABC):

    entry_point_args = {}
    entry_point_verbs = []
    entry_point_nouns = []

    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH, env_file_path: Path = DEFAULT_ENV_FILE):
        self.env_file_path = env_file_path
        self.config: RSTermConfig = parse_config(config_path)

        terminal_args = self.config.get_terminal_args()

        terminal_args.add_args(self.entry_point_args)
        terminal_args.add_nouns(self.entry_point_nouns)
        terminal_args.add_verbs(self.entry_point_verbs)

        self.cmd_args: Namespace = parse_terminal_args(terminal_args.formatted_args)

        load_app_env(self.env_file_path)

        self.db_connection: connection = None


    @abstractmethod
    def run(self) -> None:
        pass

    def set_db_connection(self, connection_name: str):
        connection_env_var = self.config.get_db_connection_string(connection_name)
        self.db_connection = get_db_connection(connection_env_var)
