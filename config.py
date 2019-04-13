#!/usr/bin/python
"""config.py: user-serviceable parts
Author: Wes Modes (wmodes@gmail.com)
Copyright: 2017, MIT """

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


debug = 3
media_base = 'media'
filmdb = 'FILM_DB.json'
logfile = '/var/log/exhibitvideo/exhibitvideo.log'
inter_video_delay = 0.25

omx_cmd = ['omxplayer', '--no-osd', '--no-keys', '--refresh', '--aspect-mode stretch']
#omx_cmd = ['omxplayer', '--no-osd', '--no-keys', '--refresh']
content_cmd = omx_cmd + ['--layer %i', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer%i']
loop_cmd = omx_cmd + ['--layer %i', '--loop', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer%i']
transition_cmd = omx_cmd + ['--layer %i', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer%i']

# A recipe for film sequencing - a list of tuples (<tag>, <length>)
# note length here, overrides db values, and 0 takes db value
# possible values: footage, interview, title, trailer
recipedb = [
    ('trailer', 0),
    ('footage', 0),

    ('interview', 0),
    ('footage', 0),
    ('title', 0),

    ('footage', 0),
    ('footage', 0),

    ('interview', 0),
    ('footage', 60),
    ('title', 0),

    # ('playful', 0),
    ('footage', 0),

    ('interview', 0),
    ('footage', 0),
]
