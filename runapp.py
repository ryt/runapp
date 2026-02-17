#!/usr/bin/env python3

__version__   = '0.1.3'
__author__    = 'Copyright (C) 2024-2026 Ray (github.com/ryt)'
__manual__    = """
runapp: Super lightweight interface for running and deploying python web apps via gunicorn.
--
Usage:

  Basic options for managing processes (in current dir)
  -----------------------------------------------------
  runapp
  runapp  start
  runapp  stop
  runapp  restart
  runapp  reload
  runapp  debug
  runapp  (list|-l)
  runapp  (all|-a)

  To manage processes with specified config and appdir
  ----------------------------------------------------
  runapp  (reload|start|stop|...)  /path/to/runapp.conf  /path/to/appdir

  Show the gunicorn or shell command and exit (for any of the above options)
  --------------------------------------------------------------------------
  runapp  ...    -s

  Show the contents of the app settings config file
  -------------------------------------------------
  runapp  (conf|-c)

  Show the running process ids (if any)
  -------------------------------------
  runapp  (pid|pids|-p)

  Enter debug mode
  ----------------
  runapp  debug

  Help manual and version
  -----------------------
  runapp  (man|help|-h|--help)
  runapp  (-v|--version)

--
""" + __author__ + """
--

"""

import os
import re
import sys
import pydoc
import itertools
from types import SimpleNamespace

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


class settings:
  """Basic settings"""
  conf_name = 'runapp.conf'
  add_suffx = 'runapp'
  load_once = True

  appsuffx  = ''
  appname   = ''
  appcall   = ''
  appuser   = ''
  appgroup  = ''
  workers   = ''
  port      = ''

  cm_start    = ''
  cm_debug    = ''
  cm_list     = ''
  cm_listall  = ''

  sslcertkey = ''



def validate_specified_configs():
  """Check if there are valid specified paths (config and appdir) in cli argument"""
  if len(sys.argv) < 4:
    return False

  specified_config = f'{os.path.dirname(sys.argv[2])}/{settings.conf_name}'
  specified_appdir = os.path.abspath(sys.argv[3])

  if not os.path.exists(specified_config):
    sys.exit(f'Sorry, the settings file ({specified_config}) could not be found.')

  if not os.path.exists(specified_appdir):
    sys.exit(f'Sorry, the specified appdir ({specified_appdir}) is not valid.')

  valid_msg = f'Valid specified settings: {specified_config}\nValid specified appdir: {specified_appdir}'

  return SimpleNamespace(
    config=specified_config,
    appdir=specified_appdir,
    msg=valid_msg,
  )


def load_conf():
  """Load and parse the config file"""

  validated_specified_config = validate_specified_configs()

  if validated_specified_config:
    conf_file = validated_specified_config.config # specified dir
  else:
    conf_file = settings.conf_name # current dir

  # -- start: run once ?? -- #
  if not settings.load_once:
    return
  settings.load_once = False
  # -- end: run once ?? -- #

  if not os.path.exists(conf_file):
    sys.exit(f'Sorry, the settings file ({settings.conf_name}) could not be found in the current dir.')

  # Specific app settings for gunicorn.
  # To prevent errors, the section [global] will be automatically added to the config.

  config = ConfigParser()
  with open(conf_file) as cf:
    config.read_file(itertools.chain(['[global]'], cf), source=conf_file)


  settings.appname   = config.get('global', 'appname')   # e.g. hellopy
  settings.appcall   = config.get('global', 'appcall')   # e.g. app:hello -> gunicorn [APP_MODULE]
  settings.appuser   = config.get('global', 'appuser')   # e.g. ray
  settings.appgroup  = config.get('global', 'appgroup')  # e.g. staff
  settings.workers   = config.get('global', 'workers')   # e.g. 2
  settings.port      = config.get('global', 'port')      # e.g. 8000

  # add suffix to appname (gunicorn -n option) for debugging
  settings.appsuffx = f'{settings.appname}-{settings.add_suffx}'

  # for gunicorn APP_MODULE, add appdir to use with --chdir option if a specified appdir is valid
  if validated_specified_config:
    settings.appcall = f'--chdir {validated_specified_config.appdir} {settings.appcall}'

  # Additional options: ssl

  settings.sslcertkey = ''

  if config.has_option('global', 'sslcertkey'):
    sslck  = config.get('global', 'sslcertkey') # e.g. /srv/ssl.crt /srv/ssl.key
    sslck  = sslck.split(' ')
    sslcertkey = f'--certfile={sslck[0]} --keyfile={sslck[1]}'

  # Main gunicorn and process list commands

  settings.cm_start = ''.join((
    f'gunicorn {sslcertkey} {settings.appcall} ',
    f'-n {settings.appsuffx} ',
    f'-w {settings.workers} ',
    f'-u {settings.appuser} ',
    f'-g {settings.appgroup} ',
    f'-b :{settings.port} -D'
  ))

  settings.cm_debug   = f'{settings.cm_start.rstrip("-D")} --log-level debug'
  settings.cm_list    = f"ps aux | grep '[{settings.appname[0:1]}]{settings.appname[1:]}'";
  settings.cm_listall = f"ps aux | grep '{settings.add_suffx}'"


def ps_aux(show_all=False):
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
  if show_all:
    cmd = settings.cm_listall
  else:
    cmd = settings.cm_list

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
  # for default (current dir)
  if len(sys.argv) > 2 and sys.argv[2] == '-s':
    sys.exit(cmd)
  
  # for specified configs
  elif len(sys.argv) > 4 and sys.argv[4] == '-s':
    sys.exit(cmd)


def run_cmd(cmd):
  """Run the command using subprocess.check_output()"""
  return check_output(cmd, shell=True, encoding='utf-8')


def process_list(show_all=False):
  load_conf()
  if show_all:
    show_cmd(settings.cm_listall)
  else:
    show_cmd(settings.cm_list)
  procs = ps_aux(show_all)
  if procs:
    if show_all:
      show_msg = f'List of all {settings.add_suffx} processes that are currently running ({len(procs)}):'
    else:
      show_msg = f'The app {settings.appname} is currently running under {len(procs)} processes at port {settings.port}:'
    print(show_msg)
    for p in procs:
      guni_path = re.sub(r'^.*\s(\/[^\s]+gunicorn).*$', '\\1', p['command'])
      add_using = f' using: {bc.OKCYAN}{guni_path}{bc.ENDC}' if 'gunicorn' in p['command'] else ''
      if show_all:
        cmd_appcall = p['command'].split(f'-{settings.add_suffx}')[0].split(' ')[-1]
        print(''.join((
          "- ",
          f"app: {cmd_appcall}-{settings.add_suffx}  ",
          f"pid: {bc.FAIL}{p['pid']}{bc.ENDC}  ",
          f"user: {p['user']}  ",
          f"start: {p['start']}  ",
          f"time: {p['time']} {add_using}"
        )))
      else:
        print(''.join((
          "- ",
          f"app: {settings.appname}  ",
          f"pid: {bc.FAIL}{p['pid']}{bc.ENDC}  ",
          f"user: {p['user']}  ",
          f"start: {p['start']}  ",
          f"time: {p['time']} {add_using}"
        )))
  else:
    print(f'No processes found for {settings.appname}. App is (most likely) not running.')


def process_start():
  load_conf()
  cmd = settings.cm_start
  show_cmd(cmd)
  pids = get_pids()
  if pids:
    print(f'The app is already running with processes. Attempting to start again.')
  print(f'Starting {settings.appname} using {settings.appcall} at port {settings.port}.')
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
  print(f'Stopping {settings.appname} and terminating {len(pids)} processes.')
  run = run_cmd(cmd)
  print(run) if run else ''
  if not pids:
    print('Nothing to stop. Be sure to double check your app configuration.')


def process_restart(input='reload'):
  load_conf()
  pids = get_pids()
  cmd = f"kill -9 {' && kill -9 '.join(pids)}" if pids else ''
  cmd = f'{cmd} && {settings.cm_start}' if pids else settings.cm_start
  show_cmd(cmd)
  print(f'Restarting {settings.appname} using {settings.appcall} at port {settings.port}.')
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
  cmd = f'{cmd} && {settings.cm_debug}' if pids else settings.cm_debug
  show_cmd(cmd)
  print('\n'.join((
    f'Running {settings.appname} in debug mode using {settings.appcall} at port {settings.port}.',
    f'Review the following for details. Ctrl/Cmd+C to exit.'
  )))
  try:
    try:
      run_cmd(cmd)
    except:
      print('')
  except CalledProcessError as e:
    print('Nothing to debug. Be sure to double check your app configuration.')


def process_conf():
  load_conf()
  with open(settings.conf_file, 'r') as conf:
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

  elif sys.argv[1] in ('all','-a'):
    return process_list(show_all=True)

  elif sys.argv[1] in ('-v','--version'):
    return print(f'Version: {__version__}')

  elif sys.argv[1] in ('help','-h','--help'):
    return print(__manual__.strip())

  elif sys.argv[1] == 'man':
    return pydoc.pager(__manual__.strip())

  else:
    print("Invalid command. Please use 'man' or 'help' for list of valid commands.")



if __name__ == '__main__':
  main()
