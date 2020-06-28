from rsterm import EntryPoint


class MyEt1(EntryPoint):

    def call(self) -> None:
        print('here is my code 1')


class MyEt2(EntryPoint):

    def call(self) -> None:
        print('here is my code 2')

