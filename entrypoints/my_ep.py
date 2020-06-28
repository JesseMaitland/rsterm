from pathlib import Path

from rsterm import EntryPoint


class DoAction(EntryPoint):

    entry_point_args = {

        ('foo', ): {
            'help': 'pass some do action foo!'
        }
    }

    def __init__(self, env_name: str = None):
        print("we are doing action")
        super().__init__(env_name)

    def run(self) -> None:
        print('here is my code 1')

