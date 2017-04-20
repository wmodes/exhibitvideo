#!/usr/bin/python
"""video.py: play and manage threaded video as needed
Author: Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)
Copyright: 2017, MIT """

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from random import choice
import threading
import os
from subprocess import call
import json

# local modules
import videothread
from common import *
import ffprobe

#
# Constants
#


#
# Globals
#

# # A list of film records 
# # (each record of which is a film dict)
# film_list = []
# # A dictionary of lists of films, indexed by type 
# # (each record of which is a film dict)
# film_dict = {}
# # A dictionary of content types, indexed by trigger
# # (each record of which is a film dict)
# content_film_dict = {}

#
# Preparatory
#

def read_film_file(filename):
    """Get JSON film file. File """
    with open(filename, 'r') as fp:
        return json_load_byteified(fp)

# json returns unicode objects, but for our purposes byte format is fine
# http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python


def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )


def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )


def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


def create_film_lists_dict(film_list):
    """Iterate through imported database and sort list by type"""
    film_dict = {}
    for film in film_list:
        filename = config.media_base + '/' + film['file']
        if 'name' in film:
            name = film['name']
        else:
            name = film['file']
        if 'disabled' in film and film['disabled']:
            debug("%s disabled. Removed from database" % name)
        elif not os.path.isfile(filename):
            debug("File %s not found. Removed from database" % filename)
        else:
            # first let's fill in necessary but missing fields
            if ('length' not in film or film['length'] == 0):
                film['length'] = get_duration(filename)
                debug("Getting duration for %s: %f" % (name, film['length']))
            # make lists of film types
            # Note, that this means a film can be in several lists
            if 'type' in film:
                type = film['type']
                if type not in film_dict: 
                    film_dict[type] = [film]
                else:
                    film_dict[type].append(film)
    return film_dict


def create_content_dict(content_list):
    """Iterate through content db and create dict keyed by trigger"""
    # look through all films in the content list
    content_dict = {}
    for film in content_list:
        # if a film has a trigger key
        if 'trigger' in film:
            # get the film's trigger value
            trigger_value = film['trigger']
            # if we have not already created an entry for this trigger_value
            if trigger_value not in content_dict:
                # create a new list entry in the content dictionary with key trigger
                content_dict[trigger_value] = [film]
            else:
                # otherwise, append film to the existing list
                content_dict[trigger_value].append(film)
    return content_dict


#
# file stuff
#

def get_duration(filename):
    debug("Getting duration of %s" % filename)
    length = ffprobe.duration(filename)
    if length == None:
        length = 0
    return length


#
# Control
#


def main():
    global film_db
    film_db = read_film_file(config.media_base + '/' + config.filmdb)
    create_film_lists()
    create_content_dict()
    try:
        loop_film = choice(loop_film_list)
        loop_thread = videothread.VideoThread([loop_film], media_dir=config.media_base, debug=config.debug)

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
            content_thread = videothread.VideoThread([trans1_film, content_film, trans2_film], 
                        media_dir=config.media_base, debug=config.debug)

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
