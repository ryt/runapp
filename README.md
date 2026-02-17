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

Additional options: Error log, SSL

```ini
sslcertkey = /srv/ssl.crt /srv/ssl.key
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
runapp debug
runapp (list|-l)
runapp (all|-a)
```

To manage processes with specified config and appdir paths:

```console
runapp  (reload|start|stop|...)  /path/to/runapp.conf  /path/to/appdir
```

To list current processes:

```console
runapp (list|-l)  # list from current dir
runapp (all|-a)   # list all runapp processes

runapp (list|-l) /path/to/runapp.conf  /path/to/appdir  # list from specified dir
```

To simply print the gunicorn or shell command used and exit, add the `-s` option as the **third** parameter to any option above.

```console
runapp ...     -s
runapp start   -s
runapp reload  -s
runapp list    -s
```
To view the app settings config file or running process ids (if any), use the following options:

```console
runapp (conf|-c)
runapp (pid|pids|-p)
```

To debug the app, use the `debug` option to enter debug mode. This will stop the running app and start a gunicorn instance in standard (non-daemon) mode and will display errors in the terminal.

```console
runapp debug
```
Once the debugging is complete, use `Ctrl/Cmd+C` to exit and restart the app normally.

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

#### Extras
**Note:** Ported from the original Perl script to Python. You can access the perl version at [ryt/runapp-perl](https://github.com/ryt/runapp-perl). 


