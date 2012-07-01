import collections
import functools
import io
import re
import struct


def synchsafe(value):
    'Takes a normal integer and returns a syncsafe integer.'
    mask = 0x7F

    while mask ^ 0x7FFFFFFF:
        result = value & ~mask
        result = result << 1
        result |= value & mask
        mask = ((mask + 1) << 8) - 1
        value = result

    return result


def unsynchsafe(value):
    'Takes a syncsafe integer and returns a normal integer.'
    result, mask = 0, 0x7F000000

    # For each byte
    while mask:
        result = result >> 1
        result |= value & mask
        mask = mask >> 8

    return result


class TextFrame:
    # These are the available choices of text encodings and terminators
    # according to the ID3v2.4.0 specification.
    encoding_schemes = {
        0x00: ('iso-8859-1', b'\x00'),
        0x01: ('utf-16',     b'\x00\x00'), # With BOM
        0x02: ('utf-16',     b'\x00\x00'), # Without BOM
        0x03: ('utf-8',      b'\x00')
    }

    def __init__(self, data):
        # The first byte of a text information frame describes the encoding.
        encoding_description_byte, data = data[0], data[1:]

        (encoding, separator) = self.encoding_schemes[encoding_description_byte]
        strings = []

        # Split from the right, to make sure that we won't break frames with
        # multiple UTF-16 encoded strings.
        for encoded_string in data.rsplit(separator):
            string = encoded_string.decode(encoding)

            # Strip and throw away the empty strings.
            string = string.strip()
            if string:
                strings.append(string)

        self.content = strings

    def __str__(self):
        if len(self.content) == 1:
            return self.content[0]
        else:
            return ', '.join(self.content)


class PictureFrame:
    # TODO: Inherit from a common ancestor of TextFrame and PictureFrame.
    encoding_schemes = {
        0x00: ('iso-8859-1', b'\x00'),
        0x01: ('utf-16',     b'\x00\x00'), # With BOM
        0x02: ('utf-16',     b'\x00\x00'), # Without BOM
        0x03: ('utf-8',      b'\x00')
    }

    picture_types = (
        'Other',
        "32x32 pixels 'file icon' (PNG only)",
        'Cover (front)',
        'Cover (back)',
        'Leaflet page',
        'Media (e.g. label side of CD)',
        'Lead artist/lead performer/soloist',
        'Artist/performer',
        'Conductor',
        'Band/Orchestra',
        'Composer',
        'Lyricist/text writer',
        'Recording Location',
        'During recording',
        'During performance',
        'Movie/video screen capture',
        'A bright coloured fish',
        'Illustration',
        'Band/artist logotype',
        'Publisher/Studio logotype'
    )

    def read_until(self, data, delim):
        buffer = b''

        while not buffer.endswith(delim):
            buffer += data.read(1)

        return buffer[:-len(delim)]

    def __init__(self, data):
        data = io.BytesIO(data)
        encoding = data.read(1)[0]

        self.mimetype = self.read_until(data, b'\x00')
        self.type = data.read(1)
        self.description = self.read_until(data, self.encoding_schemes[encoding][1])
        self.content = io.BytesIO(data.read())


class Tag:
    attr_frame = {
        'artist': 'TPE1',
        'album': 'TALB',
        'title': 'TIT2',
        'cover': 'APIC',
    }

    def __contains__(self, name):
        return self.attr_frame[name] in self.frames

    def __getattr__(self, name):
        frame_id = self.attr_frame.get(name, None)

        if not frame_id:
            raise AttributeError

        frame = self.frames.get(frame_id, None)

        if not frame:
            raise ValueError('No such frame in tag')

        return frame.body

    def __init__(self, data=b'', file=None):
        self.data = io.BytesIO(data)

        if file and not data:
            self.data = file

        self.read_header()
        self.read_frames()

    def read_header(self):
        header_data = self.data.read(10)

        signature, version, revision, flags, size = \
            struct.unpack('!3s3BI', header_data)

        if signature != b'ID3':
            raise ValueError("Couldn't find ID3 tag.")

        supported_versions = ((3, 0), (4, 0))
        if (version, revision) not in supported_versions:
            raise ValueError("ID3 version 2.{0}.{1} is not supported.".format(
                version, revision
            ))

        self.version = (version, revision)
        self.flags = flags
        self.size = unsynchsafe(size)

    def read_frames(self):
        frames = {}
        bytes_left = self.size

        # Compile the frame id pattern in advance, to make it super ultra mega fast.
        self.tag_id_pattern = re.compile(b'[A-Z0-9]{4}')

        while bytes_left >= 10:
            frame = self.read_frame()

            bytes_left -= 10

            if frame:
                frames[frame.id] = frame
                bytes_left -= frame.size
            else:
                # Seems like we've reached the padding, so let's just skip the
                # rest of the tag.
                break

        self.frames = frames

    def read_frame(self):
        data = self.data.read(10)
        id, size, flags = struct.unpack('!4sIH', data)

        if self.tag_id_pattern.match(id):
            id = id.decode('ascii')

            if self.version[0] > 3:
                size = unsynchsafe(size)

            body = self.data.read(size)

            if id.startswith('T'):
                body = TextFrame(body)

            if id == 'APIC':
                body = PictureFrame(body)

            return collections.namedtuple(
                'Frame',
                'id size flags body',
            )(id, size, flags, body)

        return None
