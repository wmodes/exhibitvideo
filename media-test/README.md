Exhibit Video Player Media Files
===

Place media files on flash drive which will be mounted in this directory

Included on the flash drive is the ``FILM_DB.json`` a JSON file which serves as 
a database for these media files.

Mandatory keys in the film db are "file" and "tags". 

Sample values for "tags" can include "loop", "feature", "interview", 
"transition" and match tags mentioned in the recipe dictionary in ``config.py``.

TODO: Move recipe into a JSON file on the flash drive.

Example film db JSON file:

    [ 
      { "file" : "Bacon Frying (Loop).mp4",
        "tags" : [ "loop" ]
      },
      { "file" : "La Crosse Boathouses (Loop).mp4",
        "tags" : [ "loop" ]
      },
      { "file" : "Launch Party Timelapse.mp4",
        "tags" : [ "feature" ]
      },
      { "file" : "peaceful morning in galena.MOV",
        "tags" : [ "transition" ]
      },
      { "file" : "Secret History - Dorris Turner - What does the river mean to you.mp4",
        "tags" : [ "interview" ]
    ]
