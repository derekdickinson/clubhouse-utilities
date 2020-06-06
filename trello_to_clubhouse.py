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

from datetime import datetime
import json
import os
import requests
import sys
import time

g_usage_string_0_s = """
This script takes input from a Trello Board's JSON export file and creates 
stories in a Clubhouse project.

This is not general purpose, but will serve my purposes. Not sure if it will 
be helpful to anyone else. Here is the mapping:

From Trello    => To Clubhouse
------------------------------
Board (& List) => Project
Card           => Story
Card Checklist => Story Tasks
Card Comments  => Story Comments

Additionally, the newly created stories are given a label of the form:
from_trello_<TrelloBoardName>_[TrelloListName]_<Year>_<Month>_<Day>_<Hour>_<Minute>_<Second>

That way, I can use the delete script to wipe out any translations that don't 
turn out how I'd like.

This translation is not very elegant in that Trello Lists are not translated to 
Clubhouse states. Instead, I just put everything in a project with the default 
state. This serves my purposes. The [TrelloListName] is optional. If it is not 
included, every card on the board is dumped into the project. If the 
[TrelloListName] is included, only cards on that list are processed. Again, this 
makes sense for me, but may not for anyone else.

The case where a Trello Card has multiple checklists is handled by creating a 
story for every Checklist. So Card <=> Stories are mostly one to one, but
occasionally extra stories will be created.

Usage: prompt$ """

g_usage_string_1_s = ''' clubhouse_project trello_board_export_file [trello_list]

Note: This script requires that the environment variable "CLUBHOUSE_API_TOKEN" 
is set to a valid Clubhouse token.'''

g_env_usage_message_s = '''
This script requires that the environment variable "CLUBHOUSE_API_TOKEN" is
set to a valid Clubhouse token.
'''

g_trello_db_d           = None
g_project_d             = None
g_project_follower_id_s = None
g_translation_label_s   = None

g_clubhouse_api_token_s = '?token='

# API URL
g_api_url_base_s = 'https://api.clubhouse.io/api/v3/'

# Get the list of projects from clubhouse.io
def get_project_l():
  # Add page loop logic here?
  # Add timeour retry logic here?
  try:
    url_s = g_api_url_base_s + 'projects' + g_clubhouse_api_token_s
    r_response_d = requests.get(url_s)
    r_response_d.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)
  return r_response_d.json()

# Create a bunch of new stories
def create_stories(p_story_l):
  # Add page loop logic here?
  # Add timeour retry logic here?
  try:
    url_s = g_api_url_base_s + 'stories/bulk' + g_clubhouse_api_token_s
    r_response_d = requests.post(url_s, json={ 'stories': p_story_l } )
    r_response_d.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)
  return r_response_d.json()

  # g_trello_db_d['checklists'][i]['id'] (contains an 'idCard' hmmm)
  #    g_trello_db_d['cards'][i]['idChecklists'][i]

  # g_trello_db_d['lists'][i]['id'] == g_trello_db_d['cards'][i]['idList']

def create_story_d(p_trello_card_d, p_trello_comment_l, p_trello_checklist_d=None):
  r_clubhouse_story_d = {}

  # print('----------------------------------------------')
  # print(json.dumps(p_trello_card_d, indent=2))
  # print(json.dumps(p_trello_comment_l, indent=2))
  # if None != p_trello_checklist_d:
  #  print(json.dumps(p_trello_checklist_d, indent=2))
  # print('----------------------------------------------')

  l_story_name_s = p_trello_card_d['name']
  if p_trello_checklist_d:
    l_story_name_s += ('- ' + p_trello_checklist_d['name'])

  # These two fields are mandatory, crash if missing
  r_clubhouse_story_d['name']      = l_story_name_s
  r_clubhouse_story_d['project_id']= g_project_d['id']

  # Now the optional parameters - Non-arrays
  if 'desc' in p_trello_card_d:
    r_clubhouse_story_d['description']=p_trello_card_d['desc']

  # Add the label concerning this translation. No other labels.
  r_clubhouse_story_d['labels'] = [ { 'name' : g_translation_label_s } ]

  # Add the checklist is appropriate
  if p_trello_checklist_d:
    l_clubhouse_tasks_l = []
    for l_check_items_d in p_trello_checklist_d['checkItems']:                   # iterate through the items in the checklist
      l_clubhouse_tasks_l.append( { 'description' : l_check_items_d['name'], 'complete' : 'false' } )
    if l_clubhouse_tasks_l:
      r_clubhouse_story_d['tasks'] = l_clubhouse_tasks_l

  # Add Commenst
  l_clubhouse_comments_l = []
  for l_trello_comment_d in p_trello_comment_l:
    l_clubhouse_comments_l.append( { 'text' : l_trello_comment_d['data']['text'] } )

  if l_clubhouse_comments_l:
    r_clubhouse_story_d['comments'] = l_clubhouse_comments_l

  if None != g_project_follower_id_s:
    r_clubhouse_story_d['owner_ids'] = [ g_project_follower_id_s ]

  # print('++++++++++++++++++++++++++++++++++++++++++++++')
  # print(json.dumps(r_clubhouse_story_d, indent=2))
  # print('++++++++++++++++++++++++++++++++++++++++++++++')

  return r_clubhouse_story_d

def main():
 
  if (len(sys.argv) < 3) or (4 < len(sys.argv)):
    # Message reflects the current name of the script
    print(g_usage_string_0_s + sys.argv[0] + g_usage_string_1_s)
    sys.exit(1)

  l_clubhouse_project_name_s = sys.argv[1]
  l_trello_db_filename_s = sys.argv[2]
  l_trello_list_name_s = sys.argv[3] if (4 == len(sys.argv)) else None

  if not os.getenv('CLUBHOUSE_API_TOKEN'):
    print(g_env_usage_message_s)
    sys.exit(1)

  global g_clubhouse_api_token_s
  g_clubhouse_api_token_s += os.getenv('CLUBHOUSE_API_TOKEN')

  # Load the trello export file
  try:
    with open(l_trello_db_filename_s, 'r') as json_file:
      global g_trello_db_d
      g_trello_db_d = json.load(json_file)
  except Exception as e: 
    print('Failure processing file named:', l_trello_db_filename_s)
    print(e)
    sys.exit(1)

  # The full project list
  global g_clubhouse_project_l
  g_clubhouse_project_l = get_project_l()

  # Pick out the one I want this board to go to
  global g_project_d
  for l_clubhouse_project_d in g_clubhouse_project_l:
    if l_clubhouse_project_name_s == l_clubhouse_project_d['name']:
      g_project_d = l_clubhouse_project_d
  
  if None==g_project_d:
    print( 'No Clubhouse Project Name match found for: ', l_clubhouse_project_name_s )
    sys.exit(1)

  if 'follower_ids' in g_project_d: 
    global g_project_follower_id_s
    g_project_follower_id_s = g_project_d['follower_ids'][0]

  # First part of creating a unique label name for translation
  global g_translation_label_s
  g_translation_label_s = 'from_trello_' + g_trello_db_d['name'].replace(" ", "_")

  # Find the Trello source list if specified
  if l_trello_list_name_s:
    g_translation_label_s += '_' + l_trello_list_name_s.replace(" ", "_")
    for l_trello_list_d in g_trello_db_d['lists']:
      if l_trello_list_name_s == l_trello_list_d['name']:
        break
    if l_trello_list_name_s != l_trello_list_d['name']:
      print( 'Could not find Trello List: ', l_trello_list_name_s )
      sys.exit(1)

  # Complete the unique label identifying this translation
  now = datetime.now()
  g_translation_label_s += now.strftime("_%Y_%m_%d_%H_%M_%S")

  print('Translation Label is:', g_translation_label_s)

  # Increment through the trello cards and create a story list
  l_story_l = []
  for l_card_d in g_trello_db_d['cards']:

    # Exclude other lists if a specific list was specified.
    if l_trello_list_name_s and (l_card_d['idList'] != l_trello_list_d['id']):
      continue

    # Will need to get all the "commentCards" to add as comments
    l_trello_comment_l = []
    for l_action_d in g_trello_db_d['actions']:
      if 'commentCard' != l_action_d['type']: # We only care about comments
        continue
      if l_action_d['data']['card']['id'] == l_card_d['id']:
        l_trello_comment_l.append(l_action_d)

    # Now process the Checklists and add the stories to l_story_l
    if [] == l_card_d['idChecklists']:
      l_story_l.append(create_story_d(l_card_d, l_trello_comment_l)) # No checklist, one story per card.
    else:
      for l_checklist_id_s in l_card_d['idChecklists']:    # One story per checklist
        for l_checklist_d in g_trello_db_d['checklists']:
          if  l_checklist_id_s == l_checklist_d['id']:
            l_story_l.append(create_story_d(l_card_d, l_trello_comment_l, l_checklist_d))
            l_trello_comment_l = [] # Only put the comments on the first card when 

  if l_story_l:
    print(json.dumps(l_story_l, indent=2))
    create_stories(l_story_l)
    print("Success!? Well, maybe you should check your Clubhouse board and see :-) => ", l_clubhouse_project_name_s)
  else:
    print("No Board/List matches found.")

if __name__ == "__main__":
  main()  