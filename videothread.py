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

INTER_VIDEO_DELAY = 0.75

OMX_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh', '--aspect-mode fill']
CONTENT_CMD = OMX_CMD + ['--layer 4', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer1']
TRANSITION_CMD = OMX_CMD + ['--layer 5', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer2']
LOOP_CMD = OMX_CMD + ['--layer 1', '--loop', '--dbus_name', 'org.mpris.MediaPlayer2.omxplayer3']

nullin = open(os.devnull, 'r')
nullout = open(os.devnull, 'w')


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
        self.media_dir = media_dir
        self.playlist = playlist
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
        filename = self.media_dir + '/' + video['file']
        if not isinstance(video, dict):
            raise ValueError(self._example)
        if 'name' in video:
            name = video['name']
        else:
            name = video['file']
        if 'disabled' in video and video['disabled']:
            self._debug("Not played:", name, "disabled")
            return
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
        # if length is too large, scale it back
        if (start + length >= filelength):
            length = filelength - start
        # store this for later
        self._current_video = video
        # debugging output
        self._debug("name: %s (%s)" % (name, filename))
        self._debug("tags: %s" % video['tags'])
        self._debug("start: %.1fs, end: %.1fs, len: %.1fs" %
                      (start, start+length, length))
        # construct the player command
        if ('loop' in video['tags']):
            my_cmd = " ".join(LOOP_CMD + [filename])
        elif ('transition' in video['tags']):
            my_cmd = " ".join(TRANSITION_CMD + ['--pos', str(start), filename])
        else: 
            my_cmd = " ".join(CONTENT_CMD + ['--pos', str(start), filename])
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
            # If tag=loop and length=0, loop forever
            if ('loop' in video['tags']):
                self._debug("Looping indefinitely for %i (%s)" % (pgid, name))
            # otherwise, wait and kill it
            else:
                self._debug("Waiting %.2fs and setting kill timer for %i (%s)" %
                            (length - INTER_VIDEO_DELAY, pgid, name))
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
        if length == None:
            length = 0
        return length



def main():
    films = [
        {'file': "test-loop.mp4",
         'tags': 'loop',
         },
        {'name': "test-content",
         'file': "test-content.mp4",
         'tags': 'content',
         'length': 10.0,
         },
        ]
    print "Starting threaded sequence"
    video = VideoThread([films[0], films[1]], debug=2)
    video.start()
    print "Sequence started"
    raw_input("Press enter to kill video")
    video.stop()

if __name__ == "__main__":
    main()