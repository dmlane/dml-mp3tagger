""" Utility classes and functions"""

import argparse
import os
import re
import shutil
import subprocess
import textwrap


class MyException(Exception):
    """Custom exception class"""

    def __init__(self, msg: str, code: int):
        self.code = code
        self.msg = msg


class RawFormatter(argparse.HelpFormatter):
    """Help formatter to split the text on newlines and indent each line"""

    def _fill_text(self, text, width, indent):
        """Split the text on newlines and indent each line"""
        return "\n".join(
            [
                textwrap.fill(line, width)
                for line in textwrap.indent(textwrap.dedent(text), indent).splitlines()
            ]
        )


class MyData:
    """Class to hold data"""

    def __init__(self, input_file, dest_dir, backup_dir, reject_dir):
        self._input_file = input_file
        self._dest_dir = dest_dir
        self._backup_dir = backup_dir
        self._reject_dir = reject_dir
        self._basedir = None
        self._album_name = None
        self._release_date = None
        self._basename = None
        self._split_filename()

    def _split_filename(self):
        """Split a file name into constituents"""
        pattern = re.search(
            r"^(.*/([^/]*))/pod_[0-9]{2}([0-9]{2})-([0-9]*)-([0-9]*)-(.*)\.mp3",
            self._input_file,
        )
        if not pattern:
            # Try files in format ../program_name/220502-My_podcast_name.mp3
            pattern = re.search(
                r"^(.*/([^/]*))/([0-9]{2})([0-9]{2})([0-9]{2})-(.*)\.mp3", self._input_file
            )
            if not pattern:
                raise MyException(code=1, msg=f"{self._input_file} - invalid file-name format")
        (self._basedir, self._album_name, year, month, day, self._basename) = pattern.groups()
        if len(year) == 4:
            year = year[2:]
        self._release_date = f"{year}{month}{day}"

    @property
    def album_dir(self):
        """Return the album directory"""
        return str(os.path.join(self._dest_dir, self._album_name))

    @property
    def reject_dir(self):
        """Return the reject directory"""
        return str(os.path.join(self._reject_dir, self._album_name))

    @property
    def reject_file(self):
        """Return the reject file"""
        fn = "pod_" + self.full_release_date + "-" + self._basename + ".mp3"
        return os.path.join(self.reject_dir, fn)

    @property
    def output_file(self):
        """Return the album file"""
        return os.path.join(self.album_dir, self._release_date + "-" + self._basename + ".mp3")

    @property
    def album_name(self):
        """Return the album name"""
        return self._album_name

    @property
    def backup_dir(self):
        """Return the backup directory"""
        return str(os.path.join(self._backup_dir, self._album_name))

    @property
    def backup_file(self):
        """Return the backup file"""
        fn = "pod_" + self.full_release_date + "-" + self._basename + ".mp3"

        return os.path.join(self.backup_dir, fn)

    @property
    def dest_dir(self):
        """Return the destination directory"""
        return self._dest_dir

    @property
    def input_file(self):
        """Return the input file"""
        return self._input_file

    @property
    def release_date(self):
        """Return the release date"""
        return self._release_date

    @property
    def full_release_date(self):
        """Return the full release date"""
        return (
            "20"
            + self._release_date[:2]
            + "-"
            + self._release_date[2:4]
            + "-"
            + self._release_date[4:]
        )

    @property
    def release_year(self):
        """Return the release year"""
        return "20" + self._release_date[:2]

    @property
    def temp_fn(self):
        """Return the temporary file name"""
        return os.path.join(self._dest_dir, "temp.mp3")

    @property
    def basename(self):
        """Return the basename"""
        return self._basename

    @property
    def all(self):
        """Return all the data - used for testing"""
        return {
            "album_dir": self.album_dir,
            "album_name": self.album_name,
            "backup_dir": self.backup_dir,
            "backup_file": self.backup_file,
            "basename": self.basename,
            "input_file": self.input_file,
            "output_file": self.output_file,
            "reject_dir": self.reject_dir,
            "reject_file": self.reject_file,
            "release_date": self.release_date,
            "release_year": self.release_year,
            "temp_fn": self.temp_fn,
        }


def copy_to_temp(md: MyData):
    """Copy the input file to a temporary file"""
    os.makedirs(md.album_dir, exist_ok=True)
    shutil.copy(md.input_file, md.temp_fn)
    return 0


def move_to_final(md: MyData):
    """Move the temporary file to the final file"""
    shutil.move(md.temp_fn, md.output_file)
    shutil.copystat(src=md.input_file, dst=md.output_file)
    return 0


def move_to_reject(md: MyData):
    """Move the input file to the reject folder"""
    os.makedirs(md.reject_dir, exist_ok=True)
    shutil.move(md.input_file, md.reject_file)
    if os.path.isfile(md.temp_fn):
        os.remove(md.temp_fn)
    return 0


def save_original_file(md: MyData):
    """Save the original file"""
    os.makedirs(md.backup_dir, exist_ok=True)
    shutil.move(md.input_file, md.backup_file)
    return 0


def remove_temp_file(md: MyData):
    """Remove the temporary file"""
    os.remove(md.temp_fn)
    return 0


def ffmpeg_recover(md: MyData):
    """Try to make mp3 readable using ffmpeg"""
    temp_file = "/tmp/mp3tagger_ffmpeg_recover.mp3"
    result = None
    try:
        try:
            print(f"\n **** Trying to recover\n{md.input_file}\nusing ffmpeg ****")
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", md.temp_fn, temp_file], check=False, capture_output=True
            )
        except FileNotFoundError as e:
            if e.errno == 2 and e.filename == "ffmpeg":
                raise MyException(code=1, msg="ffmpeg not found") from None
        if result.returncode == 0:
            shutil.move(temp_file, md.temp_fn)
            return 0
    except MyException as e:
        print(f"\n **** {e.msg} ****\n")
    # except subprocess.CalledProcessError as e:
    #     print(e)

    if os.path.isfile(temp_file):
        os.remove(temp_file)
    return 1
