# runapp.py
Super lightweight interface for running and deploying gunicorn app processes.

#### Instructions:

1. After downloading the repo, create a symlink or alias to `runapp.py` in your executable directory or bash settings to access it. Replace `{install}` with your installation directory.

```console
alias runapp='{install}/runapp.py/runapp.py'
```

2. Create or copy the `runapp.conf` file to your app directory and configure the settings.

```console
vi runapp.conf
```

Modify the settings for your app.

```ini
{ appname => hello } etc...
```


#### Usage:

```console
runapp start
runapp stop
runapp restart
runapp reload
runapp list
runapp
```


#### Notes
Ported from the original perl script version to python3. You can access the original perl version of at [ryt/runapp](https://github.com/ryt/runapp). 


<small>Copyright &copy; 2024 Ray Mentose.</small>