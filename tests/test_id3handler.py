""" test_id3handler.py"""

import os
import shutil
import subprocess

import pytest

from mp3tagger._util import MyData, MyException
from mp3tagger.id3handler import ID3Handler, derive_title

# pylint: disable=R0801
# from shutil import copy
BASE_DIR = "/tmp/mp3_tagger/tests"
BACKUP_DIR = f"{BASE_DIR}/backup"
MP3_DIR = f"{BASE_DIR}/mp3"
REJECT_DIR = f"{BASE_DIR}/rejects"
DOWNLOAD_DIR = f"{BASE_DIR}/download/testAlbum"

RESOURCE_DIR = os.path.dirname(os.path.realpath(__file__)) + "/testresources"


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Runs before and after each test"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(MP3_DIR, exist_ok=True)
    os.makedirs(REJECT_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    yield
    shutil.rmtree(BASE_DIR)


def test_id3handler_on_valid_file():
    """test id3handler"""
    shutil.copy2(src=RESOURCE_DIR + "/240229-test1.mp3", dst=DOWNLOAD_DIR + "/240229-test1.mp3")
    md = MyData(
        input_file=DOWNLOAD_DIR + "/240229-test1.mp3",
        dest_dir=MP3_DIR,
        backup_dir=BACKUP_DIR,
        reject_dir=REJECT_DIR,
    )
    expected_output = (
        f"IDv2 tag info for {md.temp_fn}\n"
        "TALB=testAlbum\n"
        "TCON=Podcast\n"
        "TDRC=2024\n"
        "TDRL=2024-02-29 00:00:00\n"
        "TIT2=240229-test1\n"
    )
    id3 = ID3Handler()

    assert id3.process_podcast(md) == 0
    # check results
    result = subprocess.run(["mid3v2", "-l", md.temp_fn], stdout=subprocess.PIPE, check=True)
    res_stdout = result.stdout.decode("utf-8")
    assert res_stdout == expected_output


def test_id3handler_on_file_without_metadata():
    """test id3handler"""
    shutil.copy2(src=RESOURCE_DIR + "/240113-bad_mp3.mp3", dst=DOWNLOAD_DIR + "/240113-bad_mp3.mp3")
    md = MyData(
        input_file=DOWNLOAD_DIR + "/240113-bad_mp3.mp3",
        dest_dir=MP3_DIR,
        backup_dir=BACKUP_DIR,
        reject_dir=REJECT_DIR,
    )

    expected_output = (
        f"IDv2 tag info for {md.temp_fn}\n"
        "TALB=testAlbum\n"
        "TCON=Podcast\n"
        "TDRC=2024\n"
        "TDRL=2024-01-13 00:00:00\n"
        "TIT2=240113-bad_mp3\n"
    )

    id3 = ID3Handler()

    assert id3.process_podcast(md) == 0
    # check results
    result = subprocess.run(["mid3v2", "-l", md.temp_fn], stdout=subprocess.PIPE, check=True)

    res_stdout = result.stdout.decode("utf-8")
    assert expected_output == res_stdout


def test_id3handler_on_non_mp3():
    """test id3handler on a non mp3 file"""
    shutil.copy2(
        src=RESOURCE_DIR + "/240131-not_a_mp3.mp3", dst=DOWNLOAD_DIR + "/240131-not_a_mp3.mp3"
    )
    md = MyData(
        input_file=DOWNLOAD_DIR + "/240131-not_a_mp3.mp3",
        dest_dir=MP3_DIR,
        backup_dir=BACKUP_DIR,
        reject_dir=REJECT_DIR,
    )

    id3 = ID3Handler()
    with pytest.raises(MyException) as inst:
        id3.process_podcast(md)
    assert str(inst.value.msg) == f"{md.input_file} is not a valid MP3"


def test_id3handler_on_invalid_date():
    """test id3handler on a file with an invalid date"""
    shutil.copy2(
        src=RESOURCE_DIR + "/240131-not_a_mp3.mp3", dst=DOWNLOAD_DIR + "/240230-anything.mp3"
    )
    md = MyData(
        input_file=DOWNLOAD_DIR + "/240230-anything.mp3",
        dest_dir=MP3_DIR,
        backup_dir=BACKUP_DIR,
        reject_dir=REJECT_DIR,
    )

    id3 = ID3Handler()
    with pytest.raises(MyException) as inst:
        id3.process_podcast(md)
    assert str(inst.value.msg) == f"Invalid release date: {md.release_date}"


def test_derive_title():
    """test derive_title"""
    input_strings = [
        "220109-title 1",
        "embedded date 01.02.20 in title 2",
        "embedded date 2021-02-01 in title 3",
        "comedy:     title 4",
        "TED:        title 5",
        "  Another -        title 6       ",
        "20220109 title 7",
    ]
    expected_results = [
        "title 1",
        "embedded date in title 2",
        "embedded date in title 3",
        "title 4",
        "title 5",
        "Another title 6",
        "title 7",
    ]
    actual_results = []
    for value in input_strings:
        actual_results.append(derive_title(value))

    assert actual_results == expected_results
