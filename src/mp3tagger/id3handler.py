"""Handle interactions with id3 tags using mutagen"""

import re
from datetime import datetime

import mutagen
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

from mp3tagger._util import MyData, MyException, copy_to_temp, ffmpeg_recover

# noinspection SpellCheckingInspection
ORIGINAL_ARTIST = ("TOPE", mutagen.id3.TOPE)
# noinspection SpellCheckingInspection
GENRE = ("TCON", mutagen.id3.TCON)
# noinspection SpellCheckingInspection
TITLE = ("TIT2", mutagen.id3.TIT2)
# noinspection SpellCheckingInspection
RELEASE_YEAR = ("TDRC", mutagen.id3.TDRC)
# noinspection SpellCheckingInspection
RELEASE_DATE = ("TDRL", mutagen.id3.TDRL)
# noinspection SpellCheckingInspection
ALBUM = ("TALB", mutagen.id3.TALB)

REQUIRED_VERSION = (2, 4, 0)


# Series of patterns to strip out of titles
TITLE_RE = [
    re.compile(r"^[0-9]*[ \-]*"),
    re.compile(r"\d{2}\.\d{2}.\d{2,4}"),
    re.compile(r"\d{2,4}-\d{2}-\d{2}"),
    re.compile(r"comedy: *"),
    re.compile(r"TED: *"),
    re.compile(r"- *"),
    re.compile(r" +$"),
]


def derive_title(title):
    """Tidy up the title"""
    for reg_exp in TITLE_RE:
        title = re.sub(reg_exp, "", title)
    title = re.sub(r" +", " ", title)
    return title


class ID3Handler:
    """Handle interactions with id3 tags"""

    dirty = False
    audio = None

    def __init__(self):
        pass

    def set_tag(self, tag, value, any_value=False):
        """Set id3 tag if not already set to correct value or any_value is True"""
        if tag[0] in self.audio.keys():
            if any_value or self.audio[tag[0]] == tag[1](encoding=3, text=value):
                return
        self.audio[tag[0]] = tag[1](encoding=3, text=value)
        self.dirty = True

    def process_podcast(self, md: MyData):
        """Update the tags and convert them to version 2.4
        release_date must be in the format YYYYMMDD
        """

        try:
            release_date = datetime.strptime(md.release_date, "%y%m%d")

        except ValueError:
            raise MyException(msg=f"Invalid release date: {md.release_date}", code=1) from None

        formatted_date = release_date.strftime("%Y-%m-%dT%H:%M:%S")
        # Copy the mp3 to a temporary file to work on
        copy_to_temp(md)
        try:
            self.audio = MP3(md.temp_fn)
        except mutagen.mp3.HeaderNotFoundError as e:
            result = ffmpeg_recover(md)
            if result != 0:
                raise MyException(msg=f"{md.input_file} is not a valid MP3", code=2) from e
            self.dirty = True
        try:
            self.audio = ID3(md.temp_fn)
        except mutagen.id3.ID3NoHeaderError:
            self.audio = ID3()
            self.dirty = True
        self.dirty = self.dirty or (self.audio.version < REQUIRED_VERSION)
        if TITLE[0] in self.audio.keys():
            title = derive_title(self.audio[TITLE[0]].text[0])
        else:
            title = md.basename
        title = md.release_date + "-" + title
        # self.set_tag(ORIGINAL_ARTIST, md.artist)
        self.set_tag(GENRE, "Podcast")
        self.set_tag(TITLE, title)
        self.set_tag(RELEASE_YEAR, md.release_year, any_value=True)
        self.set_tag(RELEASE_DATE, formatted_date)
        self.set_tag(ALBUM, md.album_name)
        if self.dirty:
            self.audio.save(md.temp_fn)

        return 0
