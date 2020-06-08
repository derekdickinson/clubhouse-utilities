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
c - Class
d - Dictionary
l - List
n - Number
s - String

'''

import json
import os
import requests
import sys

g_usage_string_0_s = """
This script creates Clubhouse stories from story templates. For each 
template matching one or more input labels, a story is created.

This can be used to create recurring stories by creating templates with 
"interval based" labels and then running this script under cron at (or a 
similar program) at the appropriate times.

That is, if you want a recurring story to be created every Monday at
9 AM: 

1. Create a template for the story with the label Monday_9AM.
2. Execute "create_by_label.py Monday_9AM" from cron every Monday at 9AM.

Usage: prompt$ """

g_usage_string_1_s = ''' label_0 [label_1 ...]

Note: This script requires that the environment variable "CLUBHOUSE_API_TOKEN" 
is set to a valid Clubhouse token.'''

g_env_usage_message_s = '''
This script requires that the environment variable "CLUBHOUSE_API_TOKEN" is
set to a valid Clubhouse token.
'''

g_url_root_s = 'https://api.clubhouse.io'
g_api_s      = '/api/v3/'
g_token_s    = 'token='

# Example for API document
# curl -X GET \
#  -H "Content-Type: application/json" \
#  -L "https://api.clubhouse.io/api/v3/entity-templates?token=$CLUBHOUSE_API_TOKEN"
  
# Get the list of templates from clubhouse.io
def get_template_l():
  try:
    l_url_s = g_url_root_s + g_api_s + 'entity-templates' + '?' + g_token_s
    r_response_d = requests.get(l_url_s)
    r_response_d.raise_for_status()
  except requests.exceptions.RequestException as l_e_c:
    print(l_e_c)
    sys.exit(1)
  return r_response_d.json()

# Extract the fields from the template to populte the new story
def story_data_from_template(p_template_d):
  r_story_data_d = {}

  l_story_contents_d = p_template_d['story_contents']

  # These two fields are mandatory, crash if missing
  r_story_data_d['name']      =l_story_contents_d['name']
  r_story_data_d['project_id']=l_story_contents_d['project_id']

  # Now the optional parameters - Non-arrays
  if "description" in l_story_contents_d:
    r_story_data_d['description']=l_story_contents_d['description']

  if "story_type" in l_story_contents_d:
    r_story_data_d['story_type']=l_story_contents_d['story_type']

  if "workflow_state_id" in l_story_contents_d:
    r_story_data_d['workflow_state_id']=l_story_contents_d['workflow_state_id']

  # Now the array's
  # There's always at least one label
  r_story_data_d['labels'] = []
  for i in range(len(l_story_contents_d['labels'])):
    r_story_data_d['labels'].append({ 'name' : l_story_contents_d['labels'][i]['name'] })

  if "tasks" in l_story_contents_d:
    r_story_data_d['tasks'] = []
    for i in range(len(l_story_contents_d['tasks'])):
      r_story_data_d['tasks'].append({ 'description' : l_story_contents_d['tasks'][i]['description'], 'complete' : l_story_contents_d['tasks'][i]['complete'] })

  if "follower_ids" in l_story_contents_d:
    r_story_data_d['follower_ids']=l_story_contents_d['follower_ids']

  if "owner_ids" in l_story_contents_d:
    r_story_data_d['owner_ids']=l_story_contents_d['owner_ids']

  return r_story_data_d
 
# curl -X POST \
#   -H "Content-Type: application/json" \
#   -d '{ "name": "foo", "project_id": 30 }' \
#   -L "https://api.clubhouse.io/api/v3/stories?token=$CLUBHOUSE_API_TOKEN"

# Create a bunch of new stories
def create_stories(p_story_l):
  try:
    l_url_s = g_url_root_s + g_api_s + 'stories/bulk' + '?' + g_token_s
    r_response_d = requests.post(l_url_s, json={ 'stories': p_story_l } )
    r_response_d.raise_for_status()
  except requests.exceptions.RequestException as l_e_c:
    print(l_e_c)
    sys.exit(1)
  return r_response_d.json()

def main():

  if (2 > len(sys.argv)) or (2 == len(sys.argv) and '--help' == sys.argv[1]):
    # Message reflects the current name of the script
    print(g_usage_string_0_s + sys.argv[0] + g_usage_string_1_s)
    sys.exit(1)

  if not os.getenv('CLUBHOUSE_API_TOKEN'):
    print(g_env_usage_message_s)
    sys.exit(1)

  global g_token_s
  g_token_s += os.getenv('CLUBHOUSE_API_TOKEN')

  l_arg_labels_l = []
  for l_cur_arg_s in sys.argv[1:]:
    l_arg_labels_l.append(l_cur_arg_s)

  # The labels passed into the script
  print('Processing Labels:', l_arg_labels_l)

  l_template_l = get_template_l()

  l_story_l = []

  for l_cur_template_d in l_template_l:
    if "story_contents" in l_cur_template_d:
      if "labels" in l_cur_template_d['story_contents']:
        for l_cur_label_d in l_cur_template_d['story_contents']['labels']:
          if l_cur_label_d['name'] in l_arg_labels_l:
            print('Adding story from template named: '+l_cur_template_d['name'])
            l_story_l.append(story_data_from_template(l_cur_template_d))

  if l_story_l:
    create_stories(l_story_l)
  else:
    print("No label matches found.")

  sys.exit(0)

if __name__ == "__main__":
  main()