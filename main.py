from pathlib import Path
from string import punctuation
from rsterm import parse_terminal_args

INI_TEMPLATE = """

[app_env]
    file_name = .env
    
[db_connections]
    default = DB_URL

[iam_roles]
    default = IAM_ROLE
    
[aws_secrets]
    key = AWS_ACCESS_KEY_ID
    secret = AWS_ACCESS_KEY_SECRET
    
[aws_buckets]
    default = S3_BUCKET
"""

terminal_args = {
    ('new',): {
        'help': 'Command to create a new config'
    },

    ('name',): {
        'help': 'The name of the new INI config to create. A dot will be automatically prepended to the file name.'
    }
}


def validate_name(name: str) -> None:
    for char in punctuation:
        if char in name:
            print(f"Punctuation marks {punctuation} are forbidden in file names. Only letters and numbers are allowed.")
            exit()


def main():
    cmd_args = parse_terminal_args(terminal_args)
    validate_name(cmd_args.name)
    ini_path = Path.cwd().absolute() / f".{cmd_args.name}"

    try:
        ini_path.touch(exist_ok=False)
        ini_path.write_text(INI_TEMPLATE)

    except FileExistsError:
        print(f"File name {cmd_args.name} already exists. Please choose another name.")
        exit()

    print(f".{cmd_args.name} was create in your projects root directory! Please configure this file.")


if __name__ == '__main__':
    main()
