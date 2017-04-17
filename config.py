#!/usr/bin/python
"""config.py: user-serviceable parts
Author: Wes Modes (wmodes@gmail.com)
Copyright: 2017, MIT """

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


DEBUG = 2
MEDIA_BASE = 'media'
FILMDB_FILE = 'FILM_DB.json'


# A recipe for film sequencing - a list of tuples (<tag>, <length>)
# note length here, overrides db values, and 0 takes db value
recipe_db = [
    ('interview', 0),
    ('loop', 120),
    ('title', 0),

    ('feature', 0),
    ('scenic', 0),

    ('interview', 0),
    ('loop', 120),
    ('title', 0),

    ('playful', 0),
    ('scenic', 0),

    ('interview', 0),
    ('scenic', 0),
]
