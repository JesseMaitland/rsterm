from pathlib import Path
from rsterm import parse_cmd_args

YML_TEMPLATE = """
rsterm:

  entrypoints:
    - terminal/entry
  
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
    }
}


def main():
    cmd_args = parse_cmd_args(terminal_args)
    config_name = "rsterm.yml"
    config_path = Path.cwd().absolute() / config_name

    try:
        config_path.touch(exist_ok=False)
        config_path.write_text(YML_TEMPLATE)

    except FileExistsError:
        print(f"File name {config_name} already exists. Please choose another name.")
        exit()

    print(f"{config_name} was created in your projects root directory! Please configure this file.")


if __name__ == '__main__':
    main()
