from rsterm import EntryPoint


class CreateFile(EntryPoint):

    def run(self) -> None:
        print("this is the best entry point")

        print(self.config.get_iam_role('redshift'))
