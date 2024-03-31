#!/usr/bin/env python3

v = '0.0.2'
c = 'Copyright (C) 2024 Ray Mentose.'
man="""
runapp: Super lightweight interface for running and deploying gunicorn app processes.
--
Usage:

  Options for managing the app in the current working directory
  -------------------------------------------------------------
  runapp
  runapp    start
  runapp    stop
  runapp    restart
  runapp    reload
  runapp    (list|-l)

  Show the gunicorn or shell command and exit (for any of the above options)
  --------------------------------------------------------------------------
  runapp    ...           -s

  Show the contents of the app settings config file
  -------------------------------------------------
  runapp    (conf|-c)

  Show the contents of the pid file
  ---------------------------------
  runapp    (pid|-p)

  Help manual and version
  -----------------------
  runapp    (man|help|-h|--help)
  runapp    (-v|--version)

--
Copyright (C) 2024 Ray Mentose. 
Latest version can be found at: https://github.com/ryt/runapp
--

"""

import os
import re
import sys
import pydoc
import requests
import itertools

from subprocess import check_output
from configparser import ConfigParser

pids_dir  = f'{os.path.expanduser("~")}/.runapp/'
conf_file = f'runapp.conf'


def load_conf():
  """Load and parse the config file"""

  if not os.path.exists(conf_file):
    sys.exit('Sorry, the settings file (runapp.conf) could not be found in the current directory.')

  global config, appname, appcall, appuser, appgroup, workers, port
  global run, exe, cme, pid_file
  global macos_add, cm_start, cm_stop, cm_list

  # Specific app settings for gunicorn. 
  # To prevent errors, the section [global] will be automatically added to the config.

  config = ConfigParser()
  with open(conf_file) as cf:
    config.read_file(itertools.chain(['[global]'], cf), source=conf_file)


  appname   = config.get('global', 'appname')   # e.g. hellopy
  appcall   = config.get('global', 'appcall')   # e.g. app:hello
  appuser   = config.get('global', 'appuser')   # e.g. ray
  appgroup  = config.get('global', 'appgroup')  # e.g. staff
  workers   = config.get('global', 'workers')   # e.g. 2
  port      = config.get('global', 'port')      # e.g. 8000

  run = ''
  exe = ''
  cme = ''

  pid_file = f'{pids_dir}{appname}.pid'

  # On MacOS (i.e. Darwin) replace long folder names with '...':

  macos_add = "--color=always | sed 's/Library.*MacOS/.../g'" if sys.platform == 'darwin' else '';

  # Main gunicorn and process list commands

  cm_start = f'gunicorn {appcall} -n {appname} -p {pids_dir+appname}.pid -w {workers} -u {appuser} -g {appgroup} -b :{port} -D';
  cm_stop  = f'kill -9 `cat {pid_file}` && rm {pid_file}';
  cm_list  = f"ps aux | grep '[{appname[0:1]}]{appname[1:]}' {macos_add}";


def ps_aux():
  """
  Reference for `ps aux` output columns: https://superuser.com/a/117921
  --
  0     1    2     3     4    5    6    7     8      9     10
  USER  PID  %CPU  %MEM  VSZ  RSS  TTY  STAT  START  TIME  COMMAND
  --
  USER    = user owning the process
  PID     = process ID of the process
  %CPU    = It is the CPU time used divided by the time the process has been running.
  %MEM    = ratio of the process’s resident set size to the physical memory on the machine
  VSZ     = virtual memory usage of entire process (in KiB)
  RSS     = resident set size, the non-swapped physical memory that a task has used (in KiB)
  TTY     = controlling tty (terminal)
  STAT    = multi-character process state
  START   = starting time or date of the process
  TIME    = cumulative CPU time
  COMMAND = command with all its arguments
  --
  """


def get_pid():
  """Load the app settings config, check the ~/.runapp/ directory, and load existing process ids (if any)"""

  load_conf()

  if os.path.exists(pids_dir) and os.path.isdir(pids_dir):
    if os.path.exists(pid_file):
      with open(pid_file, 'r') as p:
        p = p.read().strip()
      pid = p
    else:
      pid = ''
  else:
    try:
      os.mkdir(pids_dir)
      pid = ''
    except OSError as error:
      sys.exit(f'Could not create or access the ~/.runapp/ directory: {error}')

  return pid
   

def show_cmd(cmd):
  """Print the gunicorn or shell command and exit on the '-s' option"""
  if len(sys.argv) > 2 and sys.argv[2] == '-s':
    sys.exit(cmd)

def run_cmd(cmd):
  """Run the command using subprocess.check_output()"""
  return check_output(cmd, shell=True, encoding='utf-8')

def process_list():
  pid = get_pid()
  cmd = cm_list
  show_cmd(cmd)
  print(f'Listing running processes for {appname} (port {port}).')
  run = run_cmd(cmd)
  if run:
    print(run)
  else:
    print(f'No processes found for {appname}. App is currently not running.')

def process_start():
  pid = get_pid()
  cmd = cm_start
  show_cmd(cmd)
  print(f'Starting {appname} using {appcall} at port {port}.')
  run = run_cmd(cmd)
  if run:
    print(run)
  else:
    print('Nothing to start. Please double check your app configuration.')

def process_stop():
  pid = get_pid()
  cmd = cm_stop
  show_cmd(cmd)
  print(f'Stopping {appname} and unbiding from port {port}.')
  run = run_cmd(cmd)
  if run:
    print(run)
  else:
    print('Nothing to stop. Please double check your app configuration.')

def process_restart(input='reload'):
  pid = get_pid()
  cmd = f'{cm_stop} && {cm_start}'
  print(f'Restarting {appname} using {appcall} at port {port}.')
  show_cmd(cmd)
  run = run_cmd(cmd)
  if run:
    print(run)
  else:
    print('Nothing to restart. Please double check your app configuration.')

def process_conf():
  pid = get_pid()
  with open(conf_file, 'r') as conf:
    content = conf.read().strip()
  print(content)

def process_pid():
  pid = get_pid()
  print(pid)

def main():

  if len(sys.argv) == 1:
    return process_list()

  elif sys.argv[1] in ('list','-l'):
    return process_list()

  elif sys.argv[1] == 'start':
    return process_start()

  elif sys.argv[1] == 'stop':
    return process_stop()

  elif sys.argv[1] == 'restart':
    return process_restart()

  elif sys.argv[1] == 'reload':
    return process_restart('reload')

  elif sys.argv[1] in ('conf','-c'):
    return process_conf()

  elif sys.argv[1] in ('pid','-p'):
    return process_pid()

  elif sys.argv[1] in ('-v','--version'):
    return print(f'Version: {v}')

  elif sys.argv[1] in ('help','-h','--help'):
    return print(man.strip())

  elif sys.argv[1] == 'man':
    return pydoc.pager(man.strip())

  else:
    print("Invalid command. Please use 'man' or 'help' for list of valid commands.")



if __name__ == '__main__':
  main()
