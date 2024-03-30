#!/usr/bin/env python3

v = '0.0.1'
c = 'Copyright (C) 2024 Ray Mentose.'
man="""
runapp.py: Super lightweight interface for running and deploying gunicorn app processes.

--
Usage

  param[0]      param[1]
  --------      --------

  Commands for managing the app in the current working directory
  --------------------------------------------------------------
  runapp        start
  runapp        stop
  runapp        restart
  runapp        reload
  runapp        (list|-l)
  runapp

  Help manual and version
  -----------------------
  runapp     (man|help|-h|--help)
  runapp     (-v|--version)

--

"""

import os
import re
import sys
import json
import pydoc
import requests
import calendar
import datetime


def to_json(output):
  return json.dumps(output, indent=2)


def escape_for_csv(input):
  """Prepares the given input for csv output"""
  if isinstance(input, str):
    # escape a double quote (") with additional double quote ("")
    value = input.replace('"', '""')
    value = '"' + value + '"'
    return value
  else:
    return input


def preserve_keys(data, pres):
  """Preserves only the list of keys in 'pres' for given dict 'data'"""
  resp = []
  for d in data:
    resp.append({key: d[key] for key in pres if key in d})
  return resp


today = datetime.date.today()
pids_dir  = f'{os.path.expanduser("~")}/.runapp/'
conf_file = f'runapp.conf'


def main():

  if len(sys.argv) == 1:
    return print(f'listing {pids_dir}')

  elif sys.argv[1] in ('list','-l'):
    return print(f'listing {pids_dir}')

  elif sys.argv[1] in ('start'):
    return print(f'starting {pids_dir}')

  elif sys.argv[1] in ('stop','-g'):
    return print(f'stopping {pids_dir}')

  elif sys.argv[1] in ('restart'):
    return print(f'restarting {pids_dir}')

  elif sys.argv[1] in ('reload'):
    return print(f'reloading {pids_dir}')

  elif sys.argv[1] in ('-v','--version'):
    return print(f'Version: {v}')

  elif sys.argv[1] in ('-v','--version'):
    return print(f'Version: {v}')

  elif sys.argv[1] in ('help','-h','--help'):
    return print(man.strip())

  elif sys.argv[1] in ('man'):
    return pydoc.pager(man.strip())

  else:
    print("Invalid command. Please use 'man' or 'help' for list of valid commands.")



if __name__ == '__main__':
  main()
