import sys
from typing import Dict, Tuple
from abc import ABC, abstractmethod
from pathlib import Path
from argparse import ArgumentParser, Namespace
from rsterm.configs.rsterm_config import RsTermConfig


def parse_cmd_args(args_config: Dict[Tuple[str, str], Dict[str, str]], arg_index: int = 0) -> Namespace:
    """
    Parse command line args in one call, using a dict as a configuration.
    Args:
        args_config: Dict[Tuple, Dict[str, Any]] according to standard lib ArgumentParser kwargs
        arg_index:   int starting index of the arguments to be parsed from sys.argv

    Returns: Namespace
    """
    arg_parser = ArgumentParser()

    for command, options in args_config.items():
        arg_parser.add_argument(*command, **options)
    return arg_parser.parse_args(sys.argv[arg_index:])


class EntryPoint(ABC):
    """
    Base class to be used by all program entry points. If specific arguments are to be used for the
    inheriting child class, then the entry_point_args dictionary can be overridden with the format
    below

    entry_point_args = {
        ('arg or --flag', None or -f): {
            'ArgumentParser kwargs': 'ArgumentParser values'
        }
    }

    """

    # override this class dict with any arguments which apply only to this entry point
    # or which would otherwise apply to all descendant EntryPoint objects.
    entry_point_args = {}

    def __init__(self, config_path: Path = None):
        """
        Args:
            config_path: Path[Optional] if provided, must be a path to an rsterm.yml config file.
                         if not provided, will default to root/<my_app>/my_app.yml
        """
        rsterm: RsTermConfig = RsTermConfig.parse_config(config_path)

        if rsterm.override_file:
            rsterm = RsTermConfig.override_config(rsterm)

        if rsterm.load_env:
            RsTermConfig.load_rsterm_env(rsterm)

        self.rsterm = rsterm
        self.cmd_args: Namespace = parse_cmd_args(self.entry_point_args, arg_index=3)

    @abstractmethod
    def run(self) -> None:
        """
        Must be implemented by the child entry point class. This is where you put the code
        you want to execute when your command is run.
        Returns:

        """
        pass

    @classmethod
    def name(cls) -> str:
        """
        Returns: str the name of this class in snake case
        """
        name = cls.__name__
        snake = ''.join([f'_{c.lower()}' if c.isupper() else c for c in name])
        return snake.lstrip('_')

    @classmethod
    def validate_class_name(cls) -> None:
        """
        Will raise an Exception if the class name is more than 2 words. This allows the
        actions in the rsterm.yml file to be mapped to class names.
        """
        underscores = 0
        for char in cls.name():
            if char == '_':
                underscores += 1

        if underscores > 1:
            raise Exception("Class names must consists of 2 words, ideally in the format VerbNoun.")

    @classmethod
    def is_entry_point(cls) -> bool:
        """
        Used mainly for discovery, will return True if the instance of this class is a child class.
        Returns: True if this is a child class
        """
        return False if cls.__name__ == 'EntryPoint' else True
