Amplify
=======

Have you ever wanted to instantly share an awesome track or an album with a
friend of yours? Seek no more! Amplify let you stream your favourite tracks to
any webbrowser using the rendering engine webkit, such as Safari or Google
Chrome.

Amplify is written in Python 3, and acts as a HTTP-server to stream mp3s and
the associated metadata to a webkit-enabled browser.

As of today, there's no support for Python 2, but patches are welcome!

## Screenshot

![](https://raw.github.com/DrMegahertz/amplify/master/screenshot.png)

## Installation
### OS X 10.8

First of all; make sure that you have a functional
[homebrew](http://mxcl.github.com/homebrew/) installation, then install the
Python 3 formula:

    brew install python3

Make sure that `/usr/local/share/python3` is in your PATH and then execute the
following command:

    pip3 install -e "git+https://github.com/DrMegahertz/amplify#egg=amplify"

### Ubuntu 12.10 Quantal Quetzal

Installation under Ubuntu 12.10 is actually very pleasant, just execute the
following two commands and you should be all set;

    sudo apt-get install git-core python3 python3-pip
    sudo pip-3.2 install -e "git+https://github.com/DrMegahertz/amplify#egg=amplify"

### Debian 6.0 Squeeze

Installation under squeeze is a bit cumbersome, as neither distribute nor pip
comes packaged for python3.

You can install both of the packages manually by executing the following
commands as root:

    apt-get install python3
    curl http://python-distribute.org/distribute_setup.py | python3
    curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python3

You must also make sure that you use the `pip-3.1` command when installing
amplify:

    pip-3.1 install -e "git+https://github.com/DrMegahertz/amplify#egg=amplify"


### Windows 7

Install Python and Git, then download the distribute archive from PyPI.

Navigate into the unarchived directory and run the following command:

    python setup.py install

Then we can install pip and amplify:

    C:\Python33\Scripts\easy_install-3.3-script.py pip
    C:\Python33\Scripts\pip-3.3.exe install -e "git+https://github.com/DrMegahertz/amplify#egg=amplify"

## Usage

Amplify currently takes two types of inputs; either whole directories or single
mp3 tracks.

It supports the ID3v2.3 and ID3v2.4 tagging formats, with either embedded or
separate album art.

To serve a directory of tracks, just supply the path of the album as a single
argument to amplify:

    amplify ~/Music/Album

Use the following command if you're on Windows:

    python C:\Python33\Scripts\amplify "%HOMEPATH%\Music\Album"

## Configuration

Amplify listens to port 8000 by default, but you can specify any other port
with the command line option `-p`:

    amplify -p 5000 ~/Music/Album/Song.mp3

Use `-h/--help` for a list of all configuration options.
