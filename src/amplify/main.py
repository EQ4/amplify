#!/usr/bin/env python

import json
import os
import re
import shutil
import sys

from amplify import id3v2
from amplify.application import Application
from amplify.requesthandler import HttpResponse
from amplify.utils import natural_sort


app = Application(__name__)

def parse_args():
    try:
        import argparse

        parser = argparse.ArgumentParser(description='Share music with your friends.')

        parser.add_argument('-b', '--bind', default='localhost')
        parser.add_argument('-p', '--port', default=8000, type=int)
        parser.add_argument('-c', '--cover', help='Image to use as album cover')
        parser.add_argument('path', help='Path to music file or album directory')

        options = parser.parse_args()

    except ImportError:
        import optparse

        parser = optparse.OptionParser(
            'Usage: %prog [options] <path>',
            description='Share music with your friends.'
        )

        parser.add_option('-b', '--bind', default='localhost')
        parser.add_option('-p', '--port', default=8000, type=int)
        parser.add_option('-c', '--cover', help='Image to use as album cover')

        options, args = parser.parse_args()

        if not args:
            parser.error('error: the following arguments are required: path')

        options.path = args[0]

    return options

@app.route('/')
def index(request):
    root = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(root, 'templates/index.html'), 'r') as f:
        return f.read()


@app.route('/songs')
def songs(request):
    songs = []

    for index, (path, tag) in enumerate(request.album):
        song = {
            'id': index,
            'title': str(tag.title),
            'artist': str(tag.artist),
            'url': '/song/{0}'.format(index),
        }

        songs.append(song)

    return HttpResponse(json.dumps(songs).encode('utf-8'), content_type='application/json')

def parse_range(range_string):
    match = re.match(r'^(?P<unit>bytes)=(?P<start>\d+)-(?P<end>\d+)?$', range_string)

    if not match:
        raise ValueError("Couldn't parse Content-Range value")

    groups = match.groupdict()

    return (int(groups['start']),
            int(groups['end']) if groups['end'] else 0)

@app.route('/song/(\d+)')
def song(request, index):
    full_path = request.album[int(index)][0]
    content_length = os.stat(full_path).st_size
    content_start = 0
    range_requested = request.headers['range']
    headers = {}

    if range_requested:
        status_code = 206
        range_start, _range_end = parse_range(range_requested)
        content_start = range_start
        content_length -= content_start

        headers['Content-Range'] = 'bytes {0}-{1}/{2}'.format(
            range_start,
            content_length - 1,
            content_length
        )

    else:
        status_code = 200

    headers['Content-Type'] = 'audio/mpeg'

    with open(full_path, 'rb') as file:
        file.seek(content_start, 0)

        return HttpResponse(
            file.read(),
            status_code, 'audio/mpeg', content_length, headers
        )


@app.route('/cover')
def cover(request):
    request.cover.seek(0, 0)
    cover_data = request.cover.read()

    return HttpResponse(cover_data, content_type='image/jpeg')

def main():
    options = parse_args()
    cover = None
    songs = []

    # Were we given a single file?
    if os.path.isfile(options.path) and options.path.endswith("mp3"):
        with open(options.path, 'rb') as f:
            tag = id3v2.Tag(file=f)

            if 'artist' in tag and 'title' in tag:
                songs.append((options.path, tag))

            if 'cover' in tag:
                cover = tag.cover.content

    # Or an entire directory?
    elif os.path.isdir(options.path):
        potential_covers = []

        for filename in sorted(os.listdir(options.path), key=natural_sort):
            full_path = os.path.abspath(os.path.join(options.path, filename))

            if filename.endswith('.mp3'):
                with open(full_path, 'rb') as f:
                    tag = id3v2.Tag(file=f)

                    if 'artist' in tag and 'title' in tag:
                        songs.append((full_path, tag))

                    if 'cover' in tag:
                        cover = tag.cover.content

            if filename.endswith(('.jpg', '.jpeg')):
                potential_covers.append(filename)

        # Perform some futher filtering on the list of potential cover images.
        for filename in potential_covers:
            # Look for some common keywords
            if any(keyword in filename for keyword in ('cover', 'front', 'folder')):
                cover = open(os.path.join(options.path, filename), 'rb')
                break
        else:
            if potential_covers:
                # Just pick the first one
                cover = open(os.path.join(options.path, potential_covers[0]), 'rb')

    else:
        print("Couldn't read the given input.", file=sys.stderr)
        sys.exit(1)

    if options.cover:
        app.cover = open(options.cover, 'rb')
    elif cover:
        app.cover = cover
    else:
        root = os.path.dirname(os.path.abspath(__file__))
        app.cover = open(os.path.join(root, 'static/img/default-cover.png'), 'rb')

    try:
        print('Listening on http://{0}:{1}/ ...'.format(
            options.bind, options.port
        ))

        app.run(options.bind, options.port, songs)

    except KeyboardInterrupt:
        print("Exiting...")

    return 0
