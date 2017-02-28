#!/usr/bin/python
"""exhibitvideo.py: play and manage threaded video as needed
Author: Wes Modes (wmodes@gmail.com)
Copyright: 2017, MIT """

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from random import choice
import threading
import os
from subprocess import call

# local modules
import videothread
from video_db import *
from common import *


#
# Globals
#

film_lists = {}

# create a dictionary of lists - no longer needed
#content_film_dict = {}

#
# Preparatory
#

def create_film_lists():
    """Iterate through imported database and sort list by type"""
    for film in films:
        if 'disabled' not in film or not film['disabled']:
            # make lists of film types
            # Note, that this means a film can be in several lists
            if 'tags' in film:
                for tag in film['tags']:
                    if tag not in film_lists: 
                        film_lists[tag] = [film]
                    else:
                        film_lists[tag].append(film)

#
# Control
#

def main():
    create_film_lists()
    try:
        loop_film = choice(loop_film_list)
        loop_thread = videothread.VideoThread([loop_film], debug=1)

        while True:
            max_content = len(content_film_list)-1
            print ""
            next_film = raw_input("Next video (0-%i or 'q' to quit): " % max_content)
            if ('q' in next_film):
                break
            if (str.isdigit(next_film) and int(next_film) >= 0 and int(next_film) <= max_content):
                content_film = content_film_list[int(next_film)]
            elif (next_film in content_film_dict):
                content_film = choice(content_film_dict[next_film])
            else:
                continue
            trans1_film = choice(transition_film_list)
            trans2_film = choice(transition_film_list)
            content_thread = videothread.VideoThread([trans1_film, content_film, trans2_film], debug=1)

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
