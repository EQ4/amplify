Amplify
=======

Point amplify to an album or a track of your choice, and give your
friends a chance to listen to your music through a web browser.

Currently it only works with Webkit-based browsers, as they're the only ones
that can decode mp3s.

Amplify is written for Python 3. A Python 2 port is being considered.

## Screenshot

![](https://raw.github.com/DrMegahertz/amplify/master/screenshot.png)

## Installation

    $ pip install -e "git+https://github.com/DrMegahertz/amplify#egg=amplify"

## Usage:

Amplify cannot serve entire albums yet, and will thus only play the first
track of the album if you give it a directory.

    # Will search for album cover in the directory
    $ amplify ~/Music/Album/

It serves single mp3-files just fine though, as long as the album cover is
embedded within the ID3-tag:

    # Breaks if there's no album cover embedded in the given file
    $ amplify ~/Music/Album/Song.mp3

## Configuration

Amplify listens to port 8000 by default, but you can specify any other port
with the command line option `-p`:

    $ amplify -p 5000 ~/Music/Album/Song.mp3

Use `-h/--help` for a list of all configuration options.
