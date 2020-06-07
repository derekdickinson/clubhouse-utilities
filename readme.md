New project, sort of tested ...
==================================
The following programs are working with small data sets. I've only had a 
Clubhouse.io account for a few days and haven't brought very much work over 
yet. I presume that I will have to add some logic to handle larger 
data. Fortunately there appear to be some good examples online (will look at 
https://github.com/clubhouse/api-cookbook/blob/master/change-label/change_label.py
thanks in advance to wmonline :-).

**Note:** All the following scripts require that the environment variable 
"CLUBHOUSE_API_TOKEN" is set to a valid Clubhouse token.

--------------------------------------------------------------------------
Create by Label
===============
--------------------------------------------------------------------------

This script creates Clubhouse stories from story templates. For each 
template matching one or more input labels, a story is created.

This can be used to create recurring stories by creating templates with 
"interval based" labels and then running this script under cron at (or a 
similar program) at the appropriate times.

That is, if you want a recurring story to be created every Monday at
9 AM: 

1. Create a template for the story with the label Monday_9AM.
2. Execute "create_by_label.py Monday_9AM" from cron every Monday at 9AM.

**Usage:** `$ create_by_label.py label_0 [label_1 ...]`

--------------------------------------------------------------------------
Delete by Label
===============
--------------------------------------------------------------------------

This is a one-shot forced delete of multiple stories whether they were 
archived or not! All stories that contain one or more of the input labels
are deleted without confirmation.

This was created as a complement to trello_to_clubhouse.py and 
create_by_label.py. Basically, it's a way to recover if I accidentally 
create a bunch of unwanted stories.

**Usage:** `$ delete_by_label.py label_0 [label_1 ...]`

--------------------------------------------------------------------------
Clubhouse Backup
================
--------------------------------------------------------------------------

This script backs up a workspace to a set of json files. Hoping to use 
this to do regular backups to my git server. Since I am experimenting with 
batch methods, backups are necessary.

This is derived from the ClubHouse "exporter.sh" script. However, exporter.sh
doesn't back up entity-templates, story-comments, or story tasks. I needed 
these.

I haven't written the restore for this yet (will probably do it when I screw 
something up :-). Currently, the output is _pretty_ so I can easily grep it. 
Might switch to the condensed form since _pretty_ is rather wasteful.

**Usage:** `$ club_back.py [destination_subdirectory]`

**Note:** Default subdirectory is `back`

--------------------------------------------------------------------------
Trello to Clubhouse
===================
--------------------------------------------------------------------------

This script takes input from a Trello Board's JSON export file and creates 
stories in a Clubhouse project.

This is not general purpose, but will serve my purposes. Not sure if it will 
be helpful to anyone else. Here is the mapping:

From Trello    => To Clubhouse
------------------------------
* Board (& List) => Project
* Card           => Story
* Card Checklist => Story Tasks
* Card Comments  => Story Comments  

Additionally, the newly created stories are given a label of the form:  
`from_trello_<TrelloBoardName>_[TrelloListName]_<Year>_<Month>_<Day>_<Hour>_<Minute>_<Second>`

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

**Usage:** `$ trello_to_clubhouse.py clubhouse_project trello_board_export_file [trello_list]`

--------------------------------------------------------------------------
Thanks!
=======
--------------------------------------------------------------------------
Thanks to the folks providing open source to access this API. 

I read through and used very similar logic to the python examples in 
https://github.com/clubhouse/api-cookbook. Looks like these were written by 
wmonline (Willow). Thank You!

Also want to thank David Ripplinger for this wonderful example!
https://github.com/dcripplinger/pivotaltracker-clubhouse

Also, thanks to the folks who wrote the exporter.sh script that I used as a
basis for club_back.py.
https://github.com/clubhouse/exporter
