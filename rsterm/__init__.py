import dotenv
import os
import psycopg2
import pkgutil
import inspect
import yaml
import sys
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


class VerbNounMap:

    def __init__(self, verbs: Tuple[str] = None, nouns: Tuple[str] = None) -> None:
        self._args = {
            'verbs': verbs or (),
            'nouns': nouns or ()
        }

        self._formatted_actions = {

            ('verb',): {
                'help': 'The action you would like to perform',
                'choices': verbs
            },

            ('noun',): {
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
    def formatted_actions(self) -> Dict[Tuple[str], Dict[str, Any]]:
        return self._formatted_actions

    @property
    def verb_noun_map(self) -> Tuple[str]:
        return (f"{verb}_{noun}" for verb in self.verbs for noun in self.nouns)


class RSTermConfig:

    def __init__(self, **kwargs):
        self._config = kwargs

    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        self._config[key] = value

    def get_verb_noun_map(self):
        terminal_args = self._config['rsterm']['terminal']
        return VerbNounMap(verbs=terminal_args['verbs'], nouns=terminal_args['nouns'])

    def get_db_connection_string(self, connection_name: str) -> str:
        return self._config['rsterm']['db_connections'][connection_name]

    def get_aws_secrets(self) -> AWSSecrets:
        return AWSSecrets(**self._config['rsterm']['aws_secrets'])

    def get_iam_role(self, role_name: str) -> str:
        return self._config['iam_roles'][role_name]

    def get_s3_bucket(self, bucket_name: str) -> str:
        return self._config['s3_buckets'][bucket_name]

    def get_env_file_name(self, env_name: str) -> str:
        return self._config['rsterm']['environment'][env_name]

    def get_entry_points(self) -> List[Path]:
        return [Path(p) for p in self._config['rsterm']['entrypoints']]

    def parse_nouns_and_verbs(self) -> Namespace:
        arg_parser = ArgumentParser()

        for command, options in self.get_verb_noun_map().formatted_actions.items():
            arg_parser.add_argument(*command, **options)
        return arg_parser.parse_args(sys.argv[1:3])

    @classmethod
    def parse_config(cls) -> 'RSTermConfig':
        config_path: Path = Path.cwd().absolute() / 'rsterm.yml'

        if config_path.exists():
            config = yaml.safe_load(config_path.open())
            return cls(**config)


def parse_entry_args(args_config: Dict) -> Namespace:
    arg_parser = ArgumentParser()

    for command, options in args_config.items():
        arg_parser.add_argument(*command, **options)
    return arg_parser.parse_args(sys.argv[3:])


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


class EntryPoint(ABC):

    entry_point_args = {}

    def __init__(self, env_name: str = None):

        if not env_name:
            env_name = 'app_env'

        self.config: RSTermConfig = RSTermConfig.parse_config()

        self.env_file_path = Path().cwd() / self.config.get_env_file_name(env_name)

        self.cmd_args: Namespace = parse_entry_args(self.entry_point_args)

        load_app_env(self.env_file_path)

        self.db_connection: connection = None

    @classmethod
    def new(cls, env_name: str = None):
        cls._validate_class_name()
        return cls(env_name)

    @abstractmethod
    def run(self) -> None:
        pass

    @classmethod
    def name(cls) -> str:
        name = cls.__name__
        snake = ''.join([f'_{c.lower()}' if c.isupper() else c for c in name])
        return snake.lstrip('_')

    @classmethod
    def _validate_class_name(cls) -> None:
        underscores = 0
        for char in cls.name():
            if char == '_':
                underscores += 1

        if underscores > 1:
            raise Exception("Class names must consists of 2 words, in the format VerbNoun.")

    @classmethod
    def is_entrypoint(cls) -> bool:
        return False if cls.__name__ == 'EntryPoint' else True

    def set_db_connection(self, connection_name: str):
        connection_env_var = self.config.get_db_connection_string(connection_name)
        self.db_connection = get_db_connection(connection_env_var)


def collect_entry_points() -> Dict[str, EntryPoint]:
    config = RSTermConfig.parse_config()
    modules = []
    entry_points = []

    for entry_point_path in config.get_entry_points():

        # include path if we have an __init__.py file
        modules.append(import_module(entry_point_path.as_posix()))

        for _, name, _ in pkgutil.iter_modules([entry_point_path]):
            module = import_module(f"{entry_point_path.as_posix()}.{name}")
            modules.append(module)

    # look through all the modules, and find all entry point classes
    for module in modules:

        for name, obj in inspect.getmembers(module):

            if inspect.isclass(obj):

                try:
                    if obj.is_entrypoint():
                        entry_points.append(obj)
                except AttributeError:
                    pass

    return {entry_point.name(): entry_point for entry_point in entry_points}


def run_entry_point(env_name: str = None):
    entry_points = collect_entry_points()
    config = RSTermConfig.parse_config()
    ns = config.parse_nouns_and_verbs()
    key = f"{ns.verb}_{ns.noun}"

    try:
        entry_point = entry_points[key].new(env_name)
        entry_point.run()

    except KeyError:
        print("invalid command. Not yet implemented, try again.")

    finally:
        exit(0)
