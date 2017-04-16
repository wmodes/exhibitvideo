#!/usr/bin/python
"""exhibitvideo.py: play and manage threaded video as needed
Author: Wes Modes (wmodes@gmail.com)
Copyright: 2017, MIT """

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from random import choice
import os
from subprocess import call
from pprint import pformat

# local modules
import videothread
from common import *
from config import *
from video import *


#
# Globals
#



#
# Preparatory
#

def create_film_lists_dict(film_list):
    """Iterate through imported database and sort list by type"""
    film_lists_dict = {}
    for film in film_list:
        if 'disabled' not in film or not film['disabled']:
            # make lists of film types
            # Note, that this means a film can be in several lists
            if 'tags' in film:
                for tag in film['tags']:
                    if tag not in film_lists_dict: 
                        film_lists_dict[tag] = [film]
                    else:
                        film_lists_dict[tag].append(film)
    return film_lists_dict

#
# Control
#

def main():
    # setup everything
    report("Reading film database")
    film_list = read_film_file(MEDIA_BASE + '/' + FILMDB_FILE)
    debug("\nfilm_list = \n", pformat(film_list), level=2)
    film_dict = create_film_lists_dict(film_list)
    debug("\nfilm_dict = \n", pformat(film_dict), level=2)
    recipe_index = 0
    try:
        while True:
            this_recipe, duration = recipe_db[recipe_index]
            recipe_index += 1
            if recipe_index >= len(recipe_db):
                recipe_index = 0
            # max_content = len(content_film_list)-1
            # print ""
            # next_film = raw_input("Next video (0-%i or 'q' to quit): " % max_content)
            # if ('q' in next_film):
            #     break
            # if (str.isdigit(next_film) and int(next_film) >= 0 and int(next_film) <= max_content):
            #     content_film = content_film_list[int(next_film)]
            # elif (next_film in content_film_dict):
            #     content_film = choice(content_film_dict[next_film])
            # else:
            #     continue
            if this_recipe in film_dict:
                debug("Next recipe (%i): %s, duration %.2fs, %i choices" % (recipe_index,
                      this_recipe, duration, len(film_dict[this_recipe])) )
                content_film = choice(film_dict[this_recipe])
                # if we have an override duration, add to film record
                if duration:
                    content_film['length'] = duration
                debug("Selected film: %s" % content_film, debug=2)
                content_thread = videothread.VideoThread([content_film], MEDIA_BASE, debug=DEBUG)

    except KeyboardInterrupt:
        print ""
        print "Done."
        nullin = open(os.devnull, 'r')
        nullout = open(os.devnull, 'w')
        call(["killall", "-9", "omxplayer", "omxplayer.bin"], stdout=nullout, stderr=nullout)
        nullin.close()
        nullout.close()


if __name__ == "__main__":
    main()
