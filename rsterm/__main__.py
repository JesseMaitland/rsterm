from rsterm import run_entry_point
from pathlib import Path

app_name = 'rsterm'


def main():
    run_entry_point(Path(__file__).absolute().parent / f"{app_name}.yml")


if __name__ == '__main__':
    main()
