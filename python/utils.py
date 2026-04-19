"""
Utility functions for Red Ele - MyFaba Box MP3 Tool

This module provides utility functions including:
- Monkey-patch for mutagen's ID3Header to handle malformed ID3 tags
- Unbuffered stream wrapper for proper UTF-8 output handling
"""

# Support for monkey-patching mutagen's ID3Header constructor below
# Includes from mutagen/id3/_tags.py copied verbatim
import struct
from itertools import zip_longest
from mutagen._tags import Tags
from mutagen._util import DictProxy, convert_error, read_full
from mutagen.id3._util import BitPaddedInt, unsynch, ID3JunkFrameError, \
    ID3EncryptionUnsupportedError, is_valid_frame_id, error, \
    ID3NoHeaderError, ID3UnsupportedVersionError, ID3SaveConfig
from mutagen.id3._frames import TDRC, APIC, TDOR, TIME, TIPL, TORY, TDAT, Frames_2_2, \
    TextFrame, TYER, Frame, IPLS, Frames


# Monkey-patch for mutagen's ID3Header constructor
# The standard constructor raises an exception when trying to delete ID3 tags
# where the header size is not synchsafe (common in MP3s from various sources).
# Since we only need to delete all ID3 tags, we can safely ignore header quality issues.
@convert_error(IOError, error)
def id3header_constructor_monkeypatch(self, fileobj=None):
    """
    Patched constructor for mutagen.id3._tags.ID3Header.

    This version is more permissive with malformed ID3 headers,
    allowing deletion of tags even when header size is not synchsafe.

    Raises:
        ID3NoHeaderError: If no ID3 tag is found
        ID3UnsupportedVersionError: If ID3 version is not supported
        error: For other ID3-related errors
    """
    if fileobj is None:
        # For testing purposes
        self._flags = 0
        return

    fn = getattr(fileobj, "name", "<unknown>")
    data = fileobj.read(10)
    if len(data) != 10:
        raise ID3NoHeaderError("%s: too small" % fn)

    id3, vmaj, vrev, flags, size = struct.unpack('>3sBBB4s', data)
    self._flags = flags
    self.size = BitPaddedInt(size) + 10
    self.version = (2, vmaj, vrev)

    if id3 != b'ID3':
        raise ID3NoHeaderError("%r doesn't start with an ID3 tag" % fn)

    if vmaj not in [2, 3, 4]:
        raise ID3UnsupportedVersionError("%r ID3v2.%d not supported"
                                         % (fn, vmaj))

    # Monkeypatch root cause - we need to be able to delete even incorrect ID3 tags...
    #if not BitPaddedInt.has_valid_padding(size):
    #    raise error("Header size not synchsafe")

    if (self.version >= self._V24) and (flags & 0x0f):
        raise error(
            "%r has invalid flags %#02x" % (fn, flags))
    elif (self._V23 <= self.version < self._V24) and (flags & 0x1f):
        raise error(
            "%r has invalid flags %#02x" % (fn, flags))

    if self.f_extended:
        extsize_data = read_full(fileobj, 4)

        frame_id = extsize_data.decode("ascii", "replace")

        if frame_id in Frames:
            # Some tagger sets the extended header flag but
            # doesn't write an extended header; in this case, the
            # ID3 data follows immediately. Since no extended
            # header is going to be long enough to actually match
            # a frame, and if it's *not* a frame we're going to be
            # completely lost anyway, this seems to be the most
            # correct check.
            # https://github.com/quodlibet/quodlibet/issues/126
            self._flags ^= 0x40
            extsize = 0
            fileobj.seek(-4, 1)
        elif self.version >= self._V24:
            # "Where the 'Extended header size' is the size of the whole
            # extended header, stored as a 32 bit synchsafe integer."
            extsize = BitPaddedInt(extsize_data) - 4
            # Haven't seen any MP3s broken in this way, but safe to say we
            # should be able to remove ID3s on them too :-)
            # Monkey-patched out
            #if not BitPaddedInt.has_valid_padding(extsize_data):
            #    raise error(
            #        "Extended header size not synchsafe")
        else:
            # "Where the 'Extended header size', currently 6 or 10 bytes,
            # excludes itself."
            extsize = struct.unpack('>L', extsize_data)[0]

        if extsize < 0:
            raise error("invalid extended header size")

        self._extdata = read_full(fileobj, extsize)

class Unbuffered(object):
    """
    Wrapper for output streams to ensure immediate flushing.

    This is useful for GUI applications (like Gooey) to see output
    in real-time rather than buffered.
    """
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        """Write data and immediately flush the stream."""
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        """Write multiple lines and immediately flush the stream."""
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        """Delegate all other attributes to the wrapped stream."""
        return getattr(self.stream, attr)
