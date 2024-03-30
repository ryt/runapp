# runapp.py
Super lightweight interface for running and deploying gunicorn app processes.

#### Instructions:

##### Step 1

Clone the project. Then create an alias to `runapp.py` to make it accessible as `runapp` in your terminal. For detailed instructions, scroll to the [installation](#Installation) section at the bottom.

##### Step 2
After creating an alias to `runapp`, create or copy the `runapp.conf` file to your app directory for each app you want to manage and configure the settings.
    
```console
vi runapp.conf
```
    
Modify the specific options you want for your app.
    
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

> When using runapp, a directory named `~/.runapp` will automatically be created in your home directory to store the process id's for each app/process that you run. The pids will get automatically deleted whenever the process is stopped. You can use the pid number to debug any issues you may run into when deploying apps.


#### Installation

Below are 2 options creating an alias to `runapp.py`. In the following examples, replace *{install}* with the path to the directory where you cloned or downloaded the repository.

Option 1: Adding an alias in your bash config.

>Depending on your system the file could be: *~/.bashrc*, *~/.bash_aliases*, or *~/.bash_profiles*.

```console
alias runapp='{install}/runapp/runapp.py'
```

Option 2: Creating a symbolic link and adding it to the binary directory.

```console
ln -s {install}/runapp/runapp.py /usr/bin/runapp
```
> The proper binary directory may differ based on your system. It could be */usr/bin*, */usr/local/bin*, */usr/opt/bin*, etc...

#### Notes
Ported from the original perl script version to python3. You can access the original perl version of at [ryt/runapp-perl](https://github.com/ryt/runapp-perl). 


<sub>Copyright &copy; 2024 Ray Mentose.</sub>