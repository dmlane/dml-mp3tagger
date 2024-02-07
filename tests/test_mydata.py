""" Test MyData class"""

import os
import re

from mp3tagger._util import MyData

# noinspection SpellCheckingInspection
DEST_DIR = "/tmp/dest_dir"
BACKUP_DIR = "/tmp/backup_dir"
REJECT_DIR = "/tmp/reject_dir"
INPUT_DIR = os.path.dirname(os.path.realpath(__file__)) + "/testresources/mp3"


def result_string(album, file_name):
    """Generate the expected result string"""
    if file_name.startswith("pod_"):
        pattern = re.search(
            r"^pod_[0-9]{2}([0-9]{2})-([0-9]*)-([0-9]*)-(.*)\.mp3",
            file_name,
        )
    else:
        pattern = re.search(r"([0-9]{2})([0-9]{2})([0-9]{2})-(.*)\.mp3", file_name)
    (year, month, day, basename) = pattern.groups()
    short_fn = year + month + day + "-" + basename + ".mp3"
    pod_fn = f"pod_20{year}-{month}-{day}-{basename}.mp3"
    date = year + month + day
    res = {
        "album_dir": f"{DEST_DIR}/{album}",
        "album_name": album,
        "backup_dir": f"{BACKUP_DIR}/{album}",
        "backup_file": f"{BACKUP_DIR}/{album}/{pod_fn}",
        "basename": f"{short_fn[7:-4]}",
        "input_file": f"{INPUT_DIR}/{album}/{file_name}",
        "output_file": f"{DEST_DIR}/{album}/{short_fn}",
        "reject_dir": f"{REJECT_DIR}/{album}",
        "reject_file": f"{REJECT_DIR}/{album}/{pod_fn}",
        "release_date": f"{date}",
        "release_year": f"20{year}",
        "temp_fn": f"{DEST_DIR}/temp.mp3",
    }
    return res


def test_mydata_style1():
    """Test SetData style 1"""
    # noinspection SpellCheckingInspection
    file_name = "pod_2024-01-30-test_file_1"
    album_name = "SCIENTIFIC_AMERICAN"
    full_filename = INPUT_DIR + f"/{album_name}/{file_name}.mp3"
    expected_results = result_string(album_name, file_name + ".mp3")
    my_data = MyData(full_filename, DEST_DIR, BACKUP_DIR, REJECT_DIR)
    actual_results = my_data.all
    assert actual_results == expected_results


def test_mydata_style2():
    """Test SetData style 1"""
    # noinspection SpellCheckingInspection
    file_name = "240130-test_file_1"
    album_name = "MY_ALBUM"
    full_filename = INPUT_DIR + f"/{album_name}/{file_name}.mp3"
    expected_results = result_string(album_name, file_name + ".mp3")
    my_data = MyData(full_filename, DEST_DIR, BACKUP_DIR, REJECT_DIR)
    actual_results = my_data.all
    assert expected_results == actual_results
