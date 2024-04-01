# runapp.py
:atom: Super lightweight interface for running and deploying gunicorn app processes.

#### Instructions

##### Step 1

Clone the project. Then create an alias to `runapp.py` to make it accessible as `runapp` in your terminal. For details on how to do that, scroll to the [installation](#Installation) section at the bottom.

##### Step 2
Create or copy the `runapp.conf` file to your app directory and edit the settings.
    
```ini
appname  = myapp
appcall  = app:hello
appuser  = ray
appgroup = staff
workers  = 2
port     = 8000
```


#### Usage

```console
cd myapp
```

```console
runapp
runapp start
runapp stop
runapp restart
runapp reload
runapp (list|-l)
```
To simply print the gunicorn or shell command used and exit, add the `-s` option as the **third** parameter to any option above.

```console
runapp start   -s
runapp reload  -s
runapp list    -s
...
```
To view the app settings config file or running process ids (if any), use the following options:

```console
runapp (conf|-c)
runapp (pid|pids|-p)
```


#### Installation

Below are 2 options for creating an alias to `runapp.py`. In the following examples, you should replace *{install}* with the path to the directory where you cloned or downloaded this repository.

Option 1: Adding an alias in your bash config.

>Depending on your system the file could be: *~/.bashrc*, *~/.bash_aliases*, or *~/.bash_profiles*.

```bash
alias runapp='{install}/runapp/runapp.py'
```

Option 2: Creating a symbolic link and adding it to the binary directory.

```console
ln -s {install}/runapp/runapp.py /usr/bin/runapp
```
> The **bin** directory may differ based on your system. It could be */usr/bin*, */usr/local/bin*, */usr/opt/bin*, etc.

#### Notes
Ported from the original perl script version to python3. You can access the original perl version at [ryt/runapp-perl](https://github.com/ryt/runapp-perl). 


<sub>Copyright &copy; 2024 Ray Mentose.</sub>