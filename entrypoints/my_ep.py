from pathlib import Path

from rsterm import EntryPoint


class DoAction(EntryPoint):

    entry_point_args = {

        ('--foo', '-f'): {
            'help': 'pass some optional foo!'
        }
    }

    def __init__(self, config_path: Path = None, env_name: str = None):
        super().__init__(config_path, env_name)

    def run(self) -> None:
        print('here is my code 1')


class MyEt2(EntryPoint):

    def call(self) -> None:
        print('here is my code 2')

