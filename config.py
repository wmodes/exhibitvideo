#!/usr/bin/python
"""config.py: user-serviceable parts
Author: Wes Modes (wmodes@gmail.com)
Copyright: 2017, MIT """

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


debug = 2
media_base = 'media'
filmdb = 'FILM_DB.json'
logfile = '/var/log/exhibitvideo/exhibitvideo.log'
inter_video_delay = 0.25

omx_cmd = ['omxplayer', '--no-osd', '--no-keys', '--refresh', '--aspect-mode stretch']
content_cmd = omx_cmd + ['--layer %i', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer%i']
loop_cmd = omx_cmd + ['--layer %i', '--loop', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer%i']
transition_cmd = omx_cmd + ['--layer %i', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer%i']

# A recipe for film sequencing - a list of tuples (<tag>, <length>)
# note length here, overrides db values, and 0 takes db value
recipedb = [
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
