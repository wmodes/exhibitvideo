#!/usr/bin/python
"""videothread.py: Threaded, stopable video player class
Author: Wes Modes (wmodes@gmail.com)
Copyright: 2017, MIT """

# -*- coding: iso-8859-15 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import threading
import subprocess
import sys
import signal
import os
import time

# local imports
import ffprobe

#
# constants
#

INTER_VIDEO_DELAY = 0.75

OMX_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh', '--aspect-mode fill']
CONTENT_CMD = OMX_CMD + ['--layer %i', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer%i']
LOOP_CMD = OMX_CMD + ['--layer %i', '--loop', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer%i']
TRANSITION_CMD = OMX_CMD + ['--layer %i', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer%i']

nullin = open(os.devnull, 'r')
nullout = open(os.devnull, 'w')

#
# globals
#

omx_layer_content = 1
omx_layer_loop = 3
omx_layer_transition = 5
omx_player = 1



class VideoThread(threading.Thread):
    """Thread class with a stop() method. The thread itself checks
    regularly for the stopped() condition."""
    _example = """
        The class takes a list containing one or more dictionaries containing
        data about the videos to be played:
            [{'name': "loop-idle1",         # if omitted, uses 'file'
                'file': "loop-idle1.mp4",   # looks in 'mediabase' for media
                'tags': 'loop',             # loop, transition, content, etc
                'start': 0.0,               # if omitted, assumes 0
                'length': 0.0,              # if omitted, assumes duration(filename)
                'disabled': True,           # if omitted, assumes False
             },]
        """

    def __init__(self, playlist=None, media_dir=".", debug=0):
        super(VideoThread, self).__init__()
        self._stop = threading.Event()
        # passed parameters
        self.playlist = playlist
        self.media_dir = media_dir
        # internal flags and vars
        self._debug_flag = debug
        self._last_debug_caller = None
        self._current_video = None
        self._player_pgid = None

    def set_sequence(self, playlist=None):
        self.playlist = playlist

    def stop(self):
        self._debug("Stop flag set")
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def debug(self, debug_flag):
        self._debug_flag = debug_flag

    def _debug(self, *args, **kwargs):
        """Produce debug message, indenting if from same calling function"""
        level = 1
        if ("level" in kwargs):
            level = kwargs["level"]
        elif("l" in kwargs):
            level = kwargs["l"]
        if (self._debug_flag >= level):
            text = " ".join(list(map(str, args)))
            # get name of calling function
            caller = sys._getframe(1).f_code.co_name
            if (caller == self._last_debug_caller):
                print "  debug: %s: %s" % (caller, text)
            else:
                print "debug: %s: %s" % (caller, text)
            # save last calling function
            self._last_debug_caller = caller

    def run(self):
        if not isinstance(self.playlist, list):
            raise ValueError(self._example)
        for video in self.playlist:
            if not self.stopped():
                self._start_video(video)

    def _start_video(self, video):
        """Starts a video. Takes a video object """
        # add media_dir to filename
        global omx_layer_content, omx_layer_loop, omx_layer_transition, omx_player
        filename = self.media_dir + '/' + video['file']
        # check to make sure we've passed the right thing
        if not isinstance(video, dict):
            raise ValueError(self._example)
        # set video name if we have it
        if 'name' in video:
            name = video['name']
        else:
            name = video['file']
        # skip this video if disabled in db
        if 'disabled' in video and video['disabled']:
            self._debug("Not played:", name, "disabled")
            return
        #debug messages
        self._debug("Starting %s in %s" % (name, self.media_dir))
        self._debug("Video data:", video)
        # get length
        filelength = self._get_length(filename)
        if ('length' not in video or video['length'] == 0.0):
            length = filelength
        else:
            length = video['length']
        # get start
        if 'start' in video:
            start = video['start']
        else:
            start = 0.0
        # if start is too large, set it to 0
        if (start >= filelength):
            start = 0.0
        # if length is too large, scale it back, unless loop
        if (('loop' not in video['tags']) and (start + length >= filelength)):
            length = filelength - start
        # store this for later
        self._current_video = video
        # debugging output
        self._debug("name: %s (%s)" % (name, filename))
        self._debug("tags: %s" % video['tags'])
        self._debug("start: %.1fs, end: %.1fs, len: %.1fs" %
                    (start, start+length, length))
        # each time we switch to a new video, we switch the layer
        # this will effectively toggle the 3 layer variables between (1,2), (3,4), and (5,6)
        omx_layer_content = 1 if (omx_layer_content != 1) else 2
        omx_layer_loop = 3 if (omx_layer_loop != 3) else 4
        omx_layer_transition = 5 if (omx_layer_transition != 5) else 6
        # we also toggle the virtual player
        omx_player = 1 if (omx_player != 1) else 2
        # build omxplayer command
        if ('loop' in video['tags']):
            my_cmd = " ".join(LOOP_CMD + [filename]) % (omx_layer_loop, 
                              omx_player)
        elif ('transition' in video['tags']):
            my_cmd = " ".join(TRANSITION_CMD + ['--pos', str(start), filename]) % (omx_layer_transition, 
                              omx_player)
        else: 
            my_cmd = " ".join(CONTENT_CMD + ['--pos', str(start), filename]) % (omx_layer_content, 
                              omx_player)
        self._debug("cmd:", my_cmd, l=2)
        # launch the player, saving the process handle
        # TODO: after debugging, replace 'if True' with 'try' and enable 'except'
        if True:
        # try:
            proc = None
            if (self._debug_flag >= 3):
                proc = subprocess.Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin)
            else:
                proc = subprocess.Popen(my_cmd, shell=True, preexec_fn=os.setsid, stdin=nullin, stdout=nullout)
            # save this process group id
            pgid = os.getpgid(proc.pid)
            self._player_pgid = pgid
            self._debug("Starting process: %i (%s)" % (pgid, name))
            # If we have a loop
            if ('loop' in video['tags']):
                self._debug("Looping %.2fs and setting kill timer for %s (pid %i)" %
                            (length - INTER_VIDEO_DELAY, name, pgid))
            # otherwise
            else:
                self._debug("Waiting %.2fs and setting kill timer for %s (pid %i)" %
                            (length - INTER_VIDEO_DELAY, name, pgid))
            # wait in a tight loop, checking if we've received stop event or time is over
            start_time = time.time()
            while (not self.stopped() and
                   (time.time() <= start_time + length - INTER_VIDEO_DELAY)):
                pass
            threading.Timer(INTER_VIDEO_DELAY, 
                            self._stop_video, [pgid, name]).start()
        # except:
        #     self._debug("Unable to start video", name, l=0)

    def _stop_video(self, pgid, name):
        try:
            self._debug("Killing process %i (%s)" % (pgid, name))
            os.killpg(pgid, signal.SIGTERM)
            self._player_pgid = None
            self._current_video = None
        except OSError:
            self._debug("Couldn't terminate %i (%s)" % (pgid, name))
            pass

    def _get_length(self, filename):
        self._debug("Getting duration of %s" % filename)
        length = ffprobe.duration(filename)
        if length is None:
            length = 0
        return length



def main():
    media_dir = "media"
    films = [
          { "file" : "la_crosse_boathouses_loop.mp4",
            "tags" : [ "loop" ],
            "length" : 200
          },
          { "file" : "launch_party_timelapse.mp4",
            "tags" : [ "feature" ]
          },
          { "file" : "secret_history_dorris_turner_what_does_the_river_mean_to_you.mp4",
            "tags" : [ "interview" ]
          },
        ]
    for film in films:
        print "Starting threaded sequence"
        video = VideoThread([film], media_dir, debug=2)
        video.start()
        print "Sequence started"
        raw_input("Press enter to kill video")
        video.stop()

if __name__ == "__main__":
    main()
