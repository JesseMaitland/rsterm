# RSTERM

rsterm is a library which contains some simple classes and functions to help template together a terminal application
which is intended to interact with AWS redshift and S3. 

It can be integrated with the environment of an existing project by adding references in a `rsterm.yml` file in your projects 
root directory.

### Getting Started

#### Install
rsterm can be installed by using pip.
```
pip install rsterm
```

#### New Project
Once rsterm is installed, create a new configuration file. Here you will be asked if you would like to create a new ``.env`` file
if one does not exist.
```
rsterm new project <app name here>
```

If you want your terminal app to be available at the console right away, with the above command provide the ``-i`` flag
```
rsterm new project foo -i
```

Now your app has been installed using a pip egg link in your local python env. Test it by calling the help option
```
foo -h
```

You will now have the below files in your projects root directory. 
```
app
   entrypoints
     __init__.py
   __init__.py
   __main__.py
  app.yml
```

#### Environments
Refer to the ``.yml`` file for instructions on how to configure your environments. `rsterm` can be used with multiple
environment files, which must be configured in `.yml`. it acts as a simple environment variable mapper, to allow integration 
with existing projects and `.env` files.


#### Main Entry Point
The `app.py` (or whatever you called your app) serves as the main entry point to you application. Any entry point which is created
and configured in the `.yml` file will be scanned will be available at the terminal at the time of calling.

#### Creating Entry Points

Entry points are automatically collected by the main entry file and executed according to there noun / verb combinations defined
in your ``.yml`` file under the `terminal` section.

##### Example

````python
# /app/entrypoints/my_file.py

from rsterm import EntryPoint

class RunCommand(EntryPoint):

    def run(self) -> None:
        print("this is our entry point")

````

now in the ``.yml``

````yaml
terminal:
    nouns:
      - command
    verbs:
      - run
````

