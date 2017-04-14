#!/usr/bin/python
"""config.py: user-serviceable parts
Author: Wes Modes (wmodes@gmail.com)
Copyright: 2017, MIT """

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


# A recipe for film sequencing - a list of tuples (<tag>, <length>)
# note length here, overrides db values, and 0 takes db value
recipe = [
    ('transition', 0),
    ('interview', 0),
    ('transition', 0),
    ('playful', 0),
    ('transition', 0),
    ('interview', 0),
    ('transition', 0),
    ('loop', 120),
]

