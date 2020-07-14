from pathlib import Path
from rsterm import parse_cmd_args

YML_TEMPLATE = """
rsterm:

  app:
    name: {name}

  # list the directories here where the entry points for your project exist. The will be automatically collected by rsterm.
  entrypoints:
    - {name}/terminal/entry
  
  # environments are assigned names, with the file name they are to load.
  environment:
    app_env: .env
    
  # multiple connections can be added here and can later be referenced by key value
  db_connections:
    redshift: DATABASE_URL
        
  # put your iam roles for your terminal application here
  iam_roles:
    redshift: IAM_ROLE
        
 # if your project uses aws secrets directly add them here
  aws_secrets:
    key: AWS_ACCESS_KEY_ID
    secret: AWS_ACCESS_KEY_SECRET
        
  # add as many project buckets as you wish here, you can later fetch them by name      
  aws_buckets:
    redshift: S3_BUCKET

  # add your verbs and nouns here, these will be automatically be mapped to classes of the same name
  # combination. an example command would be  my-app new file. rsterm expects a pattern of noun / verb, but this is
  # not strictly enforced.
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
    },

    ('app',): {
        'help': 'the name you would like to give to your app.'
    }
}

MAIN_TEMPLATE = """
from rsterm import run_entry_point

if __name__ == "__main__":
    run_entry_point()

""".strip()


def main():
    cmd_args = parse_cmd_args(terminal_args)

    config_name = "rsterm.yml"
    config_path = Path.cwd().absolute() / config_name
    project_path = Path.cwd().absolute() / cmd_args.app
    entry_path = project_path / "terminal/entry"
    terminal_init = project_path / "terminal/__init__.py"
    main_file = Path.cwd().absolute() / f"{cmd_args.app}.py"

    try:
        config_path.touch(exist_ok=False)
        config_path.write_text(YML_TEMPLATE.format(name=cmd_args.app))
        print(f"{config_name} was created in your projects root directory! Please configure this file.")

        project_path.mkdir(parents=True, exist_ok=True)
        entry_path.mkdir(parents=True, exist_ok=True)
        terminal_init.touch(exist_ok=True)
        main_file.touch(exist_ok=True)
        main_file.write_text(MAIN_TEMPLATE)

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
