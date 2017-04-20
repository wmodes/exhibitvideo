#
# Command line use of 'ffprobe':
#
# ffprobe -loglevel quiet -print_format json \
#         -show_format    -show_streams \
#         video-file-name.mp4
#
# man ffprobe # for more information about ffprobe
#

import subprocess as sp
import json
from common import *
import config


def probe(vid_file_path):
    ''' Give a json from ffprobe command line

    @vid_file_path : The absolute (full) path of the video file, string.
    '''
    if type(vid_file_path) != str:
        debug(vid_file_path, 'Give ffprobe a full file path of the video')
        return

    command = ["ffprobe",
            "-loglevel",  "quiet",
            "-print_format", "json",
             "-show_format",
             "-show_streams",
             vid_file_path
             ]

    pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT)
    out, err = pipe.communicate()
    return json.loads(out)


def duration(vid_file_path):
    ''' Video's duration in seconds, return a float number
    '''
    _json = probe(vid_file_path)

    if 'format' in _json:
        if 'duration' in _json['format']:
            return float(_json['format']['duration'])

    if 'streams' in _json:
        # commonly stream 0 is the video
        for s in _json['streams']:
            if 'duration' in s:
                return float(s['duration'])

    # if everything didn't happen,
    # we got here because no single 'return' in the above happen.
    debug(vid_file_path, 'I found no duration')
    #return None


if __name__ == "__main__":
    video_file_path = "./test-loop.mp4"
    print "file:", video_file_path
    print "duration:", duration(video_file_path) # 10.008