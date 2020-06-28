from pathlib import Path

from rsterm import EntryPoint


class DoThing(EntryPoint):

    entry_point_args = {

        ('--foo', '-f'): {
            'help': 'pass some optional foo!'
        }
    }

    def __init__(self, env_name: str = None):
        super().__init__(env_name)

    def run(self) -> None:
        print('here is my code 1')


class DoMore(EntryPoint):

    def run(self) -> None:
        print('here is my code 2')

