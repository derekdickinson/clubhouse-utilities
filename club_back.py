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
l - List (i.e. indexed like an array)
n - Number
d - Dictionary (i.e. like an object/structure)
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

g_clubhouse_api_token_s = '?token='

g_dirpath_s = "back"

# API URL
g_api_url_base_s = 'https://api.clubhouse.io/api/v3/'

# Get the list of templates from clubhouse.io
def get_clubhouse_l(p_source_s):
  while True:
    try:
      url_s = g_api_url_base_s + p_source_s + g_clubhouse_api_token_s
      r_response_d = requests.get(url_s)
      r_response_d.raise_for_status()
    except requests.exceptions.RequestException as e:
      print(e)
      if 429 == e.errno: 
        print( 'To Many Requests Error, waiting 10 seconds ...' )
        sleep(10)
        continue
      sys.exit(1)
    return r_response_d.json()

def post_clubhouse_l(p_source_s, p_json_s):
  while True:
    try:
      url_s = g_api_url_base_s + p_source_s + g_clubhouse_api_token_s
      r_response_d = requests.post(url_s, json=p_json_s)
      r_response_d.raise_for_status()
    except requests.exceptions.RequestException as e:
      print(e)
      if 429 == e.errno: 
        print( 'To Many Requests Error, waiting 10 seconds ...' )
        sleep(10)
        continue
      sys.exit(1)
    return r_response_d.json()

def save_clubhouse_get(p_source_s):
  r_source_l = get_clubhouse_l(p_source_s)
  l_filename_s = g_dirpath_s + '/' + p_source_s + '.json'
  print( 'creating file: ' + l_filename_s)
  with open(l_filename_s, 'w') as json_file:
    json.dump({ p_source_s : r_source_l }, json_file, indent=2)    
  return r_source_l

def save_json_list(p_name_s, p_l):
  if not p_l: # ignore cases where none exist
    return
  l_filename_s = g_dirpath_s + '/' + p_name_s + '.json'
  print( 'creating file: ' + l_filename_s)
  with open(l_filename_s, 'w') as json_file:
    json.dump({ p_name_s : p_l }, json_file, indent=2)    

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
  l_source_s = 'categories'
  save_clubhouse_get(l_source_s)

  # "https://api.clubhouse.io/api/v3/entity-templates?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('entity-templates')

  # Redundant with anything?
  # "https://api.clubhouse.io/api/v3/epic-workflow?token=$CLUBHOUSE_API_TOKEN"
  save_clubhouse_get('epic-workflow')

  # "https://api.clubhouse.io/api/v3/epics?token=$CLUBHOUSE_API_TOKEN"
  l_epic_l = save_clubhouse_get('epics')

  # "https://api.clubhouse.io/api/v3/epics/{epic-public-id}/comments?token=$CLUBHOUSE_API_TOKEN"
  l_comment_l = []
  for l_epic_d in l_epic_l:
    for l_comment_id_n in l_epic_d['comment_ids']:
      l_comment_l.append(get_clubhouse_l('epics/'+str(l_epic_d['id'])+'/comments/'+str(l_comment_id_n)))

  save_json_list('epic-comments', l_comment_l)

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
  l_story_l =  post_clubhouse_l('stories/search', json.loads('{ "archived": "false" }'))
  l_story_l += post_clubhouse_l('stories/search', json.loads('{ "archived": "true"  }'))

  save_json_list('stories', l_story_l)

  #   "comment_ids":            Yes - stories/{story-public-id}/comments/{comment-public-id}
  #   "task_ids":               Yes - stories/{story-public-id}/tasks/{task-public-id}
  l_comment_l = []
  l_task_l = []
  for l_story_d in l_story_l:
    for l_comment_id_n in l_story_d['comment_ids']:
      l_comment_l.append(get_clubhouse_l('stories/'+str(l_story_d['id'])+'/comments/'+str(l_comment_id_n)))
    for l_task_id_n in l_story_d['task_ids']:
      l_task_l.append(get_clubhouse_l('stories/'+str(l_story_d['id'])+'/tasks/'+str(l_task_id_n)))

  save_json_list('story-comments', l_comment_l)
  save_json_list('story-tasks', l_task_l)


'''
  # Hmmm, do the same comment and task ids showing up for different stories?
  # Probably doesn't happen, but the code below would handle ids from 
  # different stories having the same public ids. Will see.
  l_comment_l = []
  l_comment_id_l = []
  l_task_l = []
  l_task_id_l = []
  for l_story_d in l_story_l:
    for l_comment_id_n in l_story_d['comment_ids']:
      if l_comment_id_n not in l_comment_id_l:
        l_comment_id_l.append(l_comment_id_n)
        l_comment_l.append(get_clubhouse_l('stories/'+str(l_story_d['id'])+'/comments/'+str(l_comment_id_n)))
    for l_task_id_n in l_story_d['task_ids']:
      if l_task_id_n not in l_task_id_l:
        l_task_id_l.append(l_task_id_n)
        l_task_l.append(get_clubhouse_l('stories/'+str(l_story_d['id'])+'/tasks/'+str(l_task_id_n)))
    
# Traverse these arrays from stories too?
   "story_links": [],        ? - Probably not
   "labels": [],             No - From global list labels
   "external_tickets": [],   ? - Probably not
   "mention_ids": [],        ? - Probably not
   "member_mention_ids": [], ? - Probably not
   "file_ids": [],           No - From global list files
   "external_links": [],     ? - Probably not
   "previous_iteration_ids": ? - Probably not
   "group_mention_ids": [],  ? - Probably not
   "support_tickets": [],    ? - Probably not
   "linked_file_ids": [],    ? - Probably not
'''        

if __name__ == "__main__":
  main()