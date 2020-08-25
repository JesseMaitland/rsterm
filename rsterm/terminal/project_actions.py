import subprocess
from pathlib import Path
from rsterm import EntryPoint


class NewProject(EntryPoint):
    entry_point_args = {
        ('project_name',): {
            'help': "the name of your cli application."
        },

        ('--install', '-i'): {
            'help': 'set if you want to run "pip install -e ." to make your project available on the terminal',
            'action': 'store_true'
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.validate_project_name()

        self.root = Path(__file__).absolute().parent.parent
        self.cwd = Path().cwd().absolute()

        self.template_path = self.root / "templates"
        self.rsterm_template_path = self.template_path / "rsterm_template.yml"
        self.main_template_path = self.template_path / "main_template.txt"
        self.setup_template_path = self.template_path / "setup_template.txt"

        self.setup_path = self.cwd / "setup.py"

        self.project_path = self.cwd / self.cmd_args.project_name
        self.config_path = self.project_path / f"{self.cmd_args.project_name}.yml"

        self.entry_path = self.project_path / "entrypoints"

        self.project_init = self.project_path / "__init__.py"
        self.project_main = self.project_path / "__main__.py"
        self.entry_path_init = self.entry_path / "__init__.py"

    def run(self) -> None:
        self.create_project_dirs()
        self.create_python_files()

        templated_rsterm = self.template_rsterm(self.rsterm_template_path)
        template_main = self.template_rsterm(self.main_template_path)

        self.create_rsterm_file(templated_rsterm)
        self.create_main_file(template_main)

        self.create_setup_file()
        self.install_local()

        if self.cmd_args.install:
            print(f"rsterm project setup complete. try running {self.cmd_args.project_name} on your terminal!")
        else:
            print("rsterm project setup complete!")

    def validate_project_name(self):
        disallowed_chars = '!"#$%&\'()*+,./:;<=>?@[\\]^`{|}~'
        for char in self.cmd_args.project_name:
            if char in disallowed_chars:
                raise ValueError(f"The following characters are not allowed in a project name. {disallowed_chars}")

    def create_project_dirs(self):
        self.project_path.mkdir(parents=True, exist_ok=True)
        self.entry_path.mkdir(parents=True, exist_ok=True)

    def create_python_files(self):
        self.project_init.touch(exist_ok=True)
        self.entry_path_init.touch(exist_ok=True)

    def template_rsterm(self, template_path: Path) -> str:
        content = template_path.read_text()
        return content.format(name=self.cmd_args.project_name)

    def create_rsterm_file(self, templated_rambo: str):
        self.config_path.touch(exist_ok=True)
        self.config_path.write_text(templated_rambo)

    def create_main_file(self, templated_main: str):
        self.project_main.touch(exist_ok=True)
        self.project_main.write_text(templated_main)

    def create_setup_file(self):
        console_scripts = f"{{'console_scripts': ['{self.cmd_args.project_name} = {self.cmd_args.project_name}.__main__:main']}}"
        setup_template = self.setup_template_path.read_text()
        setup_template = setup_template.format(name=self.cmd_args.project_name, console_scripts=console_scripts)
        self.setup_path.touch(exist_ok=True)
        self.setup_path.write_text(setup_template)

    def install_local(self):
        if self.cmd_args.install:
            cmd = ['pip', 'install', '-e', '.']
            subprocess.run(cmd)
