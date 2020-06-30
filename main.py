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
    redshift: S3_BUCKET

  terminal:  
    verbs:
      - new
      - list
      
    nouns:
      - file
      - configs

""".lstrip()

ENV_TEMPLATE = """
DATABASE_URL=put-your-redshift-url-here

IAM_ROLE=put-your-iam-role-here

AWS_ACCESS_KEY_ID=put-your-aws-access-key-here

AWS_ACCESS_KEY_SECRET=put-your-aws-secret-here

S3_BUCKET=put-your-s3-bucket-here
""".lstrip()

terminal_args = {
    ('new',): {
        'help': 'Command to create a new config',
        'choices': ['new']
    }
}


def main():
    _ = parse_cmd_args(terminal_args)
    config_name = "rsterm.yml"
    config_path = Path.cwd().absolute() / config_name

    try:
        config_path.touch(exist_ok=False)
        config_path.write_text(YML_TEMPLATE)
        print(f"{config_name} was created in your projects root directory! Please configure this file.")

    except FileExistsError:
        print(f"File name {config_name} already exists. File creation will be skipped.")

    # make .env file if one does not exist
    env_path = Path('.env')
    if not env_path.exists():

        while True:

            selection = input("Would you like to create a .env file? [y/n] ").lower()

            if selection not in ['y', 'n']:
                print(f"{selection} is not a valid choice.")
                continue

            elif selection == 'n':
                break

            else:
                env_path.touch()
                env_path.write_text(ENV_TEMPLATE)
                break


if __name__ == '__main__':
    main()
