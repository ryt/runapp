# runapp.py
Super lightweight interface for running and deploying gunicorn app processes.

#### Instructions:

##### Step 1

After downloading the repo, create an alias to `runapp.py` in your bash settings or create a symlink to it in your local binary (`bin`) directory. 

> Replace `{install}` with the path to your clone directory in the following examples.

Option 1: Adding an alias to bash. Depending on your system the file could be: *~/.bashrc*, *~/.bash_aliases*, or *~/.bash_profiles*.

```console
alias runapp='{install}/runapp/runapp.py'
```

Option 2: Creating a symbolic link to the binary directory.

```console
ln -s {install}/runapp/runapp.py /usr/bin/runapp
```

##### Step 2
After creating an alias to `runapp`, create or copy the `runapp.conf` file to your app directory and configure the settings.

Edit `runapp.conf` settings.
    
```console
vi runapp.conf
```
    
Modify the options you want for your app.
    
```ini
{
  appname  => 'hellopy',
  appcall  => 'app:hello',
  appuser  => 'ray',
  appgroup => 'staff',
  workers  => '2',
  port     => '8000'
}
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
Ported from the original perl script version to python3. You can access the original perl version of at [ryt/runapp-perl](https://github.com/ryt/runapp-perl). 


<sub>Copyright &copy; 2024 Ray Mentose.</sub>