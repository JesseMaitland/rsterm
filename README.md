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
rsterm new <app name here>
```

Afterwards you will have the below files in your projects root directory. 
```
app     # where this is the name you assigned to your app
    terminal
        entry
    __init__.py
app.py
rsterm.yml
.env

```

#### Environments
Refer to the ``rsterm.yml`` file for instructions on how to configure your environments. `rsterm` can be used with multiple
environment files, which must be configured in `rsterm.yml`. it acts as a simple environment variable mapper, to allow integration 
with existing projects.


#### Main Entry Point
The `app.py` (or whatever you called your app) serves as the main entry point to you application. Any entry point which is created
and configured in the `rsterm.yml` file will be scanned will be available at the terminal at the time of calling.

#### Creating Entry Points

Entry points are automatically collected by the main entry file and executed according to there noun / verb combinations


