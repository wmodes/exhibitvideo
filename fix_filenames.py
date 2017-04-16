import os
import re

media_dir = "media"
film_db = "FILM_DB.json"
exclude = [
        "README.md",
        "FILM_DB.json",
        ]


# if there are python files here OR no media files...
if not os.system('ls *.py > /dev/null') or os.system('ls *.mov'):
    # try changing to media dir
    print "Attempting to move to directory ./%s/" % media_dir
    os.chdir(media_dir)
    # how about now?
    if not os.system('ls *.py > /dev/null') or os.system('ls *.mov'):
        print "Are you in the right directory?"
        print "You want to be in the media directory."
        exit()

path  = os.getcwd()
filenames = os.listdir(path)

with open(film_db, 'r') as content_file:
    lines = content_file.readlines()

for filename in filenames:
    if filename not in exclude and not re.match(r'^\.', filename):
        new_filename = re.sub('[ \-\(\)+:]', '_', filename).lower()
        new_filename = re.sub('__*', '_', new_filename)
        new_filename = new_filename.replace('_.', '.')
        print filename, " --> ", new_filename
        os.rename(os.path.join(path, filename), os.path.join(path, new_filename))

print "\n====================="
print "Replace contents of 'FILMS_DB.json' with the following: "

for line in lines:
    m = re.search(r'["\']file["\'][ \t]*:[ \t]*["\'](.*)["\']', line)
    if m is not None:
        filename = m.group(1)
        new_filename = re.sub('[ \-\(\)+:]', '_', filename).lower()
        new_filename = re.sub('__*', '_', new_filename)
        new_filename = new_filename.replace('_.', '.')
        print line.replace(filename, new_filename),
    else:
        print line,

