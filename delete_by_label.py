#!/usr/bin/python3

'''
Copyright Derek Dickinson 2020 Open Source MIT/Expat license 
For specific text see: https://github.com/derekdickinson/utilities_clubhouse/blob/master/LICENSE.txt

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
import requests
import sys

g_usage_string_0_s = """
!!! Danger !!!

This is a one-shot forced delete of multiple stories whether they were 
archived or not! All stories that contain one or more of the input labels
are deleted without confirmation.

!!! Danger !!!

This was created as a complement to trello_to_clubhouse.py and 
create_by_label.py. Basically, it's a way to recover if I accidentally create 
a bunch of unwanted stories.

Usage: prompt$ """
g_usage_string_1_s = ''' label_0 label_1 ...

Note: This script requires that the environment variable "CLUBHOUSE_API_TOKEN" 
is set to a valid Clubhouse token.'''

g_env_usage_message_s = '''
This script requires that the environment variable "CLUBHOUSE_API_TOKEN" is
set to a valid Clubhouse token.
'''

g_clubhouse_api_token_s = '?token='

# API URL
g_api_url_base_s = 'https://api.clubhouse.io/api/v3/'

# Python variant of this example
#
# curl -X GET \
#   -H "Content-Type: application/json" \
#   -L "https://api.clubhouse.io/api/v3/labels?token=$CLUBHOUSE_API_TOKEN"

# Get the list of labels
def get_labels_l():
  try:
    url_s = g_api_url_base_s + 'labels' + g_clubhouse_api_token_s
    r_response_d = requests.get(url_s)
    r_response_d.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)
  return r_response_d.json()

# curl -X GET \
#  -H "Content-Type: application/json" \
#  -L "https://api.clubhouse.io/api/v3/labels/{label-public-id}/stories?token=$CLUBHOUSE_API_TOKEN"  

# Get the list of stories associated with the labels
def get_story_l(p_label_id_n):
  try:
    url_s = g_api_url_base_s + 'labels/'+ str(p_label_id_n) +'/stories' + g_clubhouse_api_token_s
    r_response_d = requests.get(url_s)
    r_response_d.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)
  return r_response_d.json()

# curl -X PUT \
#  -H "Content-Type: application/json" \
#  -d '{ "archived": true, "story_ids": [123] }' \
#  -L "https://api.clubhouse.io/api/v3/stories/bulk?token=$CLUBHOUSE_API_TOKEN"  

# Archive the stories
def archive_stories(p_story_l):
  try:
    url_s = g_api_url_base_s + 'stories/bulk' + g_clubhouse_api_token_s
    r_response_d = requests.put(url_s, json={ "archived": 'true', 'story_ids': p_story_l } )
    r_response_d.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)
  return 0

# curl -X DELETE \
#  -H "Content-Type: application/json" \
#  -d '{ "story_ids": [123] }' \
#  -L "https://api.clubhouse.io/api/v3/stories/bulk?token=$CLUBHOUSE_API_TOKEN"

# Delete the stories
def delete_stories(p_story_l):
  try:
    url_s = g_api_url_base_s + 'stories/bulk' + g_clubhouse_api_token_s
    r_response_d = requests.delete(url_s, json={ 'story_ids': p_story_l } )
    r_response_d.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)
  return 0

def main():

  if (2 > len(sys.argv)) or (2 == len(sys.argv) and '--help' == sys.argv[1]):
    # Message reflects the current name of the script
    print(g_usage_string_0_s + sys.argv[0] + g_usage_string_1_s)
    sys.exit(1)

  if not os.getenv('CLUBHOUSE_API_TOKEN'):
    print(g_env_usage_message_s)
    sys.exit(1)

  global g_clubhouse_api_token_s
  g_clubhouse_api_token_s += os.getenv('CLUBHOUSE_API_TOKEN')

  l_arg_labels_l = []
  for l_cur_arg_s in sys.argv[1:]:
    l_arg_labels_l.append(l_cur_arg_s)

  # The labels passed into the script
  print('Processing Labels:', l_arg_labels_l)

  # All the labels for the user's workspaces
  l_labels_l = get_labels_l()

  l_label_ids_l = []
  for l_cur_label_d in l_labels_l:
    if l_cur_label_d['name'] in l_arg_labels_l:
      l_label_ids_l.append(l_cur_label_d['id'])

  # These labels are not used anywhere.
  if not l_label_ids_l:
    print("These labels are not used.")
    sys.exit(1)

  l_story_id_l = []
  for l_cur_label_id_n in l_label_ids_l:
    l_story_l = get_story_l(l_cur_label_id_n)
    for l_story_d in l_story_l:
      if l_story_d['id'] not in l_story_id_l:
        l_story_id_l.append(l_story_d['id'])

  if l_story_id_l:
    print("Deleting Stories with Ids:", json.dumps(l_story_id_l))
    archive_stories(l_story_id_l) # Delete will fail unless the story is archived
    delete_stories(l_story_id_l)
  else:
    print("No Story matches for these labels.")

  sys.exit(0)

if __name__ == "__main__":
  main()
