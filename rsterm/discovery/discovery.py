import pkgutil
import inspect
from typing import Dict
from importlib import import_module
from pathlib import Path
from rsterm.entrypoint.entrypoint import EntryPoint
from rsterm.configs.rsterm_config import RsTermConfig


def collect_entry_points(config_path: Path = None) -> Dict[str, EntryPoint]:
    """
    function is used to introspect and collect all EntryPoint classes from the paths
    configured in the rambo.yml file.

    Returns: Dict[str, EntryPoint]
        The return dictionary contains all classes which have inherited from EntryPoint,
        with a corresponding name key. This key is used as a verb_noun_mapping.
    """
    config = RsTermConfig.parse_config(config_path)
    entry_points = []

    if config.is_pip_package:
        project_path = getattr(import_module(config.app_name), '__path__')[0]
    else:
        project_path = Path(config.app_name).absolute().as_posix()

    for entrypoint_path in config.entrypoint_paths:
        doted_path = entrypoint_path.replace('/', '.')

        for _, name, _ in pkgutil.iter_modules([f"{project_path}/{entrypoint_path}"]):

            if config.is_pip_package:
                module = import_module(name=f".{name}", package=f"{config.app_name}.{doted_path}")
            else:
                module = import_module(doted_path)

            for mod_name, obj in inspect.getmembers(module):

                if inspect.isclass(obj) and issubclass(obj, EntryPoint):

                    if obj.is_entry_point():
                        entry_points.append(obj)
    return {entry_point.name(): entry_point for entry_point in entry_points}


def run_entry_point(config_path: Path = None):
    """
    function introspects all entry point paths as specified in the rsterm.yml file, and collects all
    objects which have inherited from EntryPoint, and maps them to the verb / noun mappings as specified
    in rambo.yml If a mapping combination exists in the config file, but there is no corresponding class
    name, then a NotImplementedError is raised, and the function prints an error message and exits.
    """
    entry_points = collect_entry_points(config_path)
    config = RsTermConfig.parse_config(config_path)
    ns = config.parse_nouns_and_verbs()
    key = f"{ns.verb}_{ns.noun}"
    exit_code = 0

    try:
        if key not in entry_points.keys():
            raise NotImplementedError
        else:
            entry_point = entry_points[key].new(config_path)
            entry_point.run()

    except NotImplementedError:
        print("invalid command. Not yet implemented, try again.")
        exit_code = 1

    exit(exit_code)  # exit no matter what
