#!/usr/bin/python3

'''
Copyright Derek Dickinson 2020 Open Source MIT/Expat license 
For specific text see: https://github.com/derekdickinson/utilities_clubhouse/blob/master/LICENSE.txt

This is derived from the ClubHouse "exporter.sh" script.

Variable Naming Convention: 

Names are of the form: S_varname_T

S indicates Scope (mostly): 
g - Global variables "g_"
l - Local variables "l_"
p - Parameters "p_"
r - Return values "r_"

T indicates Type:
c - Class
d - Dictionary
l - List
n - Number
s - String

'''

import json
import os
import pathlib
import requests
import sys
import time

g_usage_string_0_s = """
This script backs up a workspace to a set of json files. Hoping to use 
this to do regular backups to my git server. Since I am experimenting with 
batch methods, backups are necessary.

By default, this will create and use a subdirectory named: 'back'
The lone parameter overrides the subdirectory name.

Usage: prompt$ """

g_usage_string_1_s = ''' [destination_subdirectory]

Note: This script requires that the environment variable "CLUBHOUSE_API_TOKEN" 
is set to a valid Clubhouse token.'''

g_env_usage_message_s = '''
This script requires that the environment variable "CLUBHOUSE_API_TOKEN" is
set to a valid Clubhouse token.
'''

g_clubhouse_api_token_s = 'token='

g_dirpath_s = "back"

# Get the list of templates from clubhouse.io
def get_clubhouse_l(p_source_s):
  while True:
    try:
      l_url_s = 'https://api.clubhouse.io/api/v3/' + p_source_s + '?' + g_clubhouse_api_token_s
      r_response_d = requests.get(l_url_s)
      r_response_d.raise_for_status()
    except requests.exceptions.RequestException as l_e_c:
      print(l_e_c)
      if 429 == l_e_c.errno: 
        print( 'To Many Requests Error, waiting 10 seconds ...' )
        sleep(10)
        continue
      sys.exit(1)
    return r_response_d.json()

def post_clubhouse_l(p_source_s, p_json_s):
  while True:
    try:
      l_url_s = 'https://api.clubhouse.io/api/v3/' + p_source_s + '?' + g_clubhouse_api_token_s
      r_response_d = requests.post(l_url_s, json=p_json_s)
      r_response_d.raise_for_status()
    except requests.exceptions.RequestException as l_e_c:
      print(l_e_c)
      if 429 == l_e_c.errno: 
        print( 'To Many Requests Error, waiting 10 seconds ...' )
        sleep(10)
        continue
      sys.exit(1)
    return r_response_d.json()

def next_query_d(p_next_s):
  while True:
    try:
      l_url_s = 'https://api.clubhouse.io' + p_next_s + '&' + g_clubhouse_api_token_s
      r_response_d = requests.get(l_url_s)
      r_response_d.raise_for_status()
    except requests.exceptions.RequestException as l_e_c:
      print(l_e_c)
      if 429 == l_e_c.errno: 
        print( 'To Many Requests Error, waiting 10 seconds ...' )
        sleep(10)
        continue
      sys.exit(1)
    return r_response_d.json()

def first_query_d(p_type_s, p_query_d):
  while True:
    try:
      l_url_s = 'https://api.clubhouse.io/api/v3/search/' + p_type_s + '?' + g_clubhouse_api_token_s
      r_response_d = requests.get(l_url_s, params=p_query_d)
      r_response_d.raise_for_status()
    except requests.exceptions.RequestException as l_e_c:
      print(l_e_c)
      if 429 == l_e_c.errno: 
        print( 'To Many Requests Error, waiting 10 seconds ...' )
        sleep(10)
        continue
      sys.exit(1)
    return r_response_d.json()

def query_clubhouse_d(p_type_s, p_query_d):
  r_story_l = []

  l_results_d = first_query_d(p_type_s, p_query_d)
  while l_results_d['next'] is not None:
    r_story_l += l_results_d['data']
    l_results_d = next_query_d(l_results_d['next'])
  else:
    r_story_l += l_results_d['data']

  return r_story_l

def save_json_list(p_name_s, p_l):
  if not p_l: # ignore cases where none exist
    return
  l_filename_s = g_dirpath_s + '/' + p_name_s + '.json'
  print( 'creating file: ' + l_filename_s)
  with open(l_filename_s, 'w') as json_file:
    json.dump({ p_name_s : p_l }, json_file)    

def save_clubhouse_get(p_source_s):
  r_source_l = get_clubhouse_l(p_source_s)
  save_json_list(p_source_s, r_source_l)
  return r_source_l

def get_epics_l():
  # A list to store each page of search results for processing.
  r_epic_l = []

  # Unarchived stories
  l_query_d = {'query': '!is:done archived:"false"', 'page_size': 25}
  r_epic_l = query_clubhouse_d('epics', l_query_d)

  # Archived stories
  # l_query_d = {'query': '!is:done archived:"true"', 'page_size': 25}
  # r_epic_l += query_clubhouse_d('epics', l_query_d)

  return r_epic_l

def get_stories_l():
  # A list to store each page of search results for processing.
  r_story_l = []

  # Unarchived stories
  l_query_d = {'query': '!is:done archived:"false"', 'page_size': 25}
  r_story_l = query_clubhouse_d('stories', l_query_d)

  # Archived stories - Getting the unarchived ones here too?
  l_query_d = {'query': '!is:done archived:"true"', 'page_size': 25}
  r_story_l += query_clubhouse_d('stories', l_query_d)

  return r_story_l

def main():

  if (2 < len(sys.argv)) or (2 == len(sys.argv) and '--help' == sys.argv[1]):
    print(g_usage_string_0_s + sys.argv[0] + g_usage_string_1_s)
    sys.exit(1)

  if 2 == len(sys.argv):
    global g_dirpath_s
    g_dirpath_s = sys.argv[1]
    try:
      pathlib.Path(g_dirpath_s).mkdir(parents=True, exist_ok=True)
    except:
      print( 'Could not create directory: ' + g_dirpath_s)
      print(g_usage_string_0_s + sys.argv[0] + g_usage_string_1_s)
      sys.exit(1)

  if not os.getenv('CLUBHOUSE_API_TOKEN'):
    print(g_env_usage_message_s)
    sys.exit(1)

  global g_clubhouse_api_token_s
  g_clubhouse_api_token_s += os.getenv('CLUBHOUSE_API_TOKEN')

  # Defaults to 'data'. Make sure it exists.
  pathlib.Path(g_dirpath_s).mkdir(parents=True, exist_ok=True)

  # Gets

  # "https://api.clubhouse.io/api/v3/categories?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('categories')

  # "https://api.clubhouse.io/api/v3/entity-templates?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('entity-templates')

  # Redundant with anything?
  # "https://api.clubhouse.io/api/v3/epic-workflow?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('epic-workflow')

  l_epic_l = get_epics_l()
  save_json_list('epics', l_epic_l)
  
  # "https://api.clubhouse.io/api/v3/files?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('files')

  # "https://api.clubhouse.io/api/v3/groups?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('groups')

  # "https://api.clubhouse.io/api/v3/iterations?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('iterations')

  # "https://api.clubhouse.io/api/v3/labels?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('labels')

  # "https://api.clubhouse.io/api/v3/linked-files?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('linked-files')

  # "https://api.clubhouse.io/api/v3/members?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('members')

  # "https://api.clubhouse.io/api/v3/milestones?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('milestones')

  # "https://api.clubhouse.io/api/v3/projects?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('projects')

  # "https://api.clubhouse.io/api/v3/repositories?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('repositories')

  # "https://api.clubhouse.io/api/v3/teams?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('teams')

  # "https://api.clubhouse.io/api/v3/workflows?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('workflows')

  # Story Searches
  l_story_l = get_stories_l()
  save_json_list('stories', l_story_l)

if __name__ == "__main__":
  main()