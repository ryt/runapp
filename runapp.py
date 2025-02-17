#!/usr/bin/env python3

v = '0.1.1'
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
  runapp    debug
  runapp    (list|-l)

  Show the gunicorn or shell command and exit (for any of the above options)
  --------------------------------------------------------------------------
  runapp    ...           -s

  Show the contents of the app settings config file
  -------------------------------------------------
  runapp    (conf|-c)

  Show the running process ids (if any)
  -------------------------------------
  runapp    (pid|pids|-p)

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
import itertools

from subprocess import check_output, CalledProcessError
from configparser import ConfigParser


class bc:
  """Colors for terminal output: https://stackoverflow.com/a/287944"""
  HEADER    = '\033[95m'
  OKBLUE    = '\033[94m'
  OKCYAN    = '\033[96m'
  OKGREEN   = '\033[92m'
  WARNING   = '\033[93m'
  FAIL      = '\033[91m'
  ENDC      = '\033[0m'
  BOLD      = '\033[1m'
  UNDERLINE = '\033[4m'


conf_file = f'runapp.conf'
load_once = True


def load_conf():
  """Load and parse the config file"""

  # -- start: run once
  global load_once
  if not load_once:
    return ''
  load_once = False
  # -- end: run once

  if not os.path.exists(conf_file):
    sys.exit('Sorry, the settings file (runapp.conf) could not be found in the current directory.')

  global config, appname, appcall, appuser, appgroup, workers, port
  global cm_start, cm_debug, cm_list, error_log

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


  # Additional options: error_log, ssl

  error_log  = 'error.log'
  sslcertkey = ''

  if config.has_option('global', 'error_log'):
    error_log = config.get('global', 'error_log') # e.g. error.log or custom

  if config.has_option('global', 'sslcertkey'):
    sslck  = config.get('global', 'sslcertkey') # e.g. /srv/ssl.crt /srv/ssl.key
    sslck  = sslck.split(' ')
    sslcertkey = f'--certfile={sslck[0]} --keyfile={sslck[1]}'

  # Main gunicorn and process list commands

  cm_start = f'gunicorn {sslcertkey} {appcall} -n {appname} -w {workers} -u {appuser} -g {appgroup} -b :{port} -D'
  cm_debug = f'{cm_start.rstrip("-D")} --error-logfile {error_log}'
  cm_list  = f"ps aux | grep '[{appname[0:1]}]{appname[1:]}'";


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
  global cm_list
  cmd = cm_list

  try:
    out = check_output(cmd, shell=True, encoding='utf-8')
  except CalledProcessError as e:
    return []

  out = re.sub(' +', ' ', out).strip()
  out_list  = out.split('\n')
  out_list  = [line.split(' ', 10) for line in out_list]
  proc_list = []

  if out_list:
    for line in out_list:
      # important: the process has to be a gunicorn (or related) process
      if 'gunicorn' in line[10]:
        proc_list.append({
          'user'    : line[0],
          'pid'     : line[1],
          'cpu'     : line[2],
          'mem'     : line[3],
          'start'   : line[7],
          'time'    : line[9],
          'command' : line[10],
        })

  return proc_list


def get_pids():
  """Check running processes and get existing process ids (if any)"""
  pids = []
  procs = ps_aux()
  if procs:
    for p in procs:
      pids.append(p['pid'])

  return pids
   

def show_cmd(cmd):
  """Print the gunicorn or shell command and exit on the '-s' option"""
  if len(sys.argv) > 2 and sys.argv[2] == '-s':
    sys.exit(cmd)

def run_cmd(cmd):
  """Run the command using subprocess.check_output()"""
  return check_output(cmd, shell=True, encoding='utf-8')

def process_list():
  load_conf()
  show_cmd(cm_list)
  procs = ps_aux()
  if procs:
    print(f'The app {appname} is currently running under {len(procs)} processes at port {port}.')
    for p in procs:
      guni_path = re.sub(r'^.*\s(\/[^\s]+gunicorn).*$', '\\1', p['command'])
      add_using = f' using: {bc.OKCYAN}{guni_path}{bc.ENDC}' if 'gunicorn' in p['command'] else ''
      print(f"- app: {appname}  pid: {bc.FAIL}{p['pid']}{bc.ENDC}  user: {p['user']}  start: {p['start']}  time: {p['time']} {add_using}")
  else:
    print(f'No processes found for {appname}. App is (most likely) not running.')

def process_start():
  load_conf()
  cmd = cm_start
  show_cmd(cmd)
  pids = get_pids()
  if pids:
    print(f'The app is already running with processes. Attempting to start again.')
  print(f'Starting {appname} using {appcall} at port {port}.')
  try:
    run = run_cmd(cmd)
    print(run) if run else ''
    process_list()
  except CalledProcessError as e:
    print('Nothing to start. Be sure to double check your app configuration.')
    

def process_stop():
  load_conf()
  pids = get_pids()
  cmd = f"kill -9 {' && kill -9 '.join(pids)}" if pids else ''
  show_cmd(cmd)
  print(f'Stopping {appname} and terminating {len(pids)} processes.')
  run = run_cmd(cmd)
  print(run) if run else ''
  if not pids:
    print('Nothing to stop. Be sure to double check your app configuration.')

def process_restart(input='reload'):
  load_conf()
  pids = get_pids()
  cmd = f"kill -9 {' && kill -9 '.join(pids)}" if pids else ''
  cmd = f'{cmd} && {cm_start}' if pids else cm_start
  show_cmd(cmd)
  print(f'Restarting {appname} using {appcall} at port {port}.')
  try:
    run = run_cmd(cmd)
    print(run) if run else ''
    process_list()
  except CalledProcessError as e:
    print('Nothing to restart. Be sure to double check your app configuration.')

def process_debug():
  load_conf()
  pids = get_pids()
  cmd = f"kill -9 {' && kill -9 '.join(pids)}" if pids else ''
  cmd = f'{cmd} && {cm_debug}' if pids else cm_debug
  show_cmd(cmd)
  print(f'Running {appname} in debug mode using {appcall} at port {port}. Review {error_log} for details. Ctrl/Cmd+C to exit.')
  try:
    try:
      run_cmd(cmd)
    except:
      print('')
  except CalledProcessError as e:
    print('Nothing to debug. Be sure to double check your app configuration.')

def process_conf():
  load_conf()
  with open(conf_file, 'r') as conf:
    content = conf.read().strip()
  print(content)

def process_pid():
  load_conf()
  pids = get_pids()
  print(f'{bc.FAIL}' + f'{bc.ENDC} {bc.FAIL}'.join(pids) + f'{bc.ENDC}')

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

  elif sys.argv[1] == 'debug':
    return process_debug()

  elif sys.argv[1] in ('conf','-c'):
    return process_conf()

  elif sys.argv[1] in ('pids','pid','-p'):
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
