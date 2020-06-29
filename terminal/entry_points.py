from rsterm import EntryPoint


class CreateFoo(EntryPoint):

    entry_point_args = {
        ('--foo', '-f'): {
            'help': 'this is where we have some awesome foo sauce!'
        }
    }

    def run(self) -> None:
        print(self.cmd_args.foo)
        print("we doin some good foo!")
