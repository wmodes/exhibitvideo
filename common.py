#!/usr/bin/python
"""common.py: common functions for exhibitvideo video player system
Author: Wes Modes (wmodes@gmail.com)
Copyright: 2017, MIT"""

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__appname__ = "exhibitvideo.py"
__author__  = "Wes Modes <wmodes@gmail.com>"
__version__ = "1.0pre0"
__license__ = "MIT"

from time import sleep, time
import sys
import logging
import warnings

# local modules
import config


#
# Globals
#

# we only report each error periodically,
# so we keep a record of last report time
last_report_time = {}
# report interval in seconds
report_interval = 5

# we only report each DEBUG msg periodically,
# so we keep a record of last debug time
last_debug_time = {}
# report interval in seconds
debug_interval = 1
# last function that called debug
debug_last_caller = ""

# create logger 
logger = logging.getLogger(__appname__)
logging.basicConfig(filename=config.logfile, level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
warnings.filterwarnings('ignore')

def report(*args):
    """immediately report information.
    Note: Accepts multiple arguments"""
    text = " ".join(list(map(str, args)))
    #print text
    logger.info(text)


def debug(*args, **kargs):
    """Produce debug message, indenting if from same calling function"""
    global debug_last_caller
    if 'level' in kargs:
        level = kargs['level']
    else:
        level = 1
    if (level <= config.debug):
        text = " ".join(list(map(str, args)))
        caller = sys._getframe(1).f_code.co_name
        # if now is greater than our last debug time + an interval
        if (text not in last_debug_time or
                time() > last_debug_time[text] + debug_interval):
            if (caller == debug_last_caller):
                report("    debug: %s: %s" % (caller, text))
            else:
                report("debug: %s: %s" % (caller, text))
            last_debug_time[text] = time()
        debug_last_caller = caller


def update(*args):
    """periodically report information at report_interval seconds.
    Note: Accepts multiple arguments"""
    text = " ".join(list(map(str, args)))
    # if now is greater than our last report time + an interval
    if (text not in last_report_time or
            time() > last_report_time[text] + report_interval):
        report(text)
        last_report_time[text] = time()
