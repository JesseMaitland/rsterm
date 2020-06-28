from pathlib import Path
from string import punctuation
from rsterm import parse_terminal_args

YML_TEMPLATE = """
rsterm:

  entrypoints:
    - entry.terminal
  
  environment:
    app_env: .env
    
    db_connections:
      redshift: DATABASE_URL
        
    iam_roles:
      redshift: IAM_ROLE
        
    aws_secrets:
      key: AWS_ACCESS_KEY_ID
      secret: AWS_ACCESS_KEY_SECRET
        
    aws_buckets:
      redshift: S3_BUCKETS

  terminal:  
    verbs:
      - new
      - list
      
    nouns:
      - file
      - configs

""".lstrip()

terminal_args = {
    ('new',): {
        'help': 'Command to create a new config',
        'choices': ['new']
    },

    ('--name', '-n'): {
        'help': 'The name of the new YML config to create. The yml extension will be appended to the name automatically',
        'default': 'rsterm'
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
    config_name = f"{cmd_args.name}.yml"
    ini_path = Path.cwd().absolute() / config_name

    try:
        ini_path.touch(exist_ok=False)
        ini_path.write_text(YML_TEMPLATE)

    except FileExistsError:
        print(f"File name {config_name} already exists. Please choose another name.")
        exit()

    print(f"{config_name} was created in your projects root directory! Please configure this file.")


if __name__ == '__main__':
    main()
