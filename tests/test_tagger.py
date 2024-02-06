""" Test the overall functionality """

import glob
import os
import shutil

import pytest

from mp3tagger.tagger import Mp3Tagger

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


def get_files():
    """Get a list of files below our BASE_DIR"""
    return sorted(glob.glob(pathname=f"{BASE_DIR}/**/*.mp3", recursive=True))


def test_good_file_keeping_original(monkeypatch):
    """Test processing of a good file"""
    shutil.copy2(src=RESOURCE_DIR + "/240229-test1.mp3", dst=DOWNLOAD_DIR + "/240229-test1.mp3")
    monkeypatch.setattr("sys.argv", ["tagger.py", "-c", RESOURCE_DIR + "/mp3tagger.ini"])
    expected_files = sorted(
        [
            f"{DOWNLOAD_DIR}/240229-test1.mp3",
            f"{MP3_DIR}/testAlbum/240229-test1.mp3",
        ]
    )
    cc = Mp3Tagger()
    cc.run()
    actual_files = get_files()
    assert actual_files == expected_files


def test_good_file_removing_original(monkeypatch):
    """Test processing of a good file"""
    shutil.copy2(src=RESOURCE_DIR + "/240229-test1.mp3", dst=DOWNLOAD_DIR + "/240229-test1.mp3")
    monkeypatch.setattr("sys.argv", ["tagger.py", "-r", "-c", RESOURCE_DIR + "/mp3tagger.ini"])
    expected_files = sorted(
        [
            f"{BACKUP_DIR}/testAlbum/240229-test1.mp3",
            f"{MP3_DIR}/testAlbum/240229-test1.mp3",
        ]
    )
    cc = Mp3Tagger()
    cc.run()
    actual_files = get_files()
    assert actual_files == expected_files


def test_non_mp3(monkeypatch):
    """Test processing of a good file"""

    shutil.copy2(
        src=RESOURCE_DIR + "/240131-not_a_mp3.mp3", dst=DOWNLOAD_DIR + "/240131-not_a_mp3.mp3"
    )
    monkeypatch.setattr("sys.argv", ["tagger.py", "-r", "-c", RESOURCE_DIR + "/mp3tagger.ini"])
    expected_files = sorted(
        [
            f"{REJECT_DIR}/testAlbum/240131-not_a_mp3.mp3",
        ]
    )
    cc = Mp3Tagger()
    cc.run()
    actual_files = get_files()
    assert actual_files == expected_files


def test_mp3_with_invalid_date(monkeypatch):
    """Test processing of a good file"""
    shutil.copy2(
        src=RESOURCE_DIR + "/240131-not_a_mp3.mp3", dst=DOWNLOAD_DIR + "/240230-anything.mp3"
    )
    monkeypatch.setattr("sys.argv", ["tagger.py", "-r", "-c", RESOURCE_DIR + "/mp3tagger.ini"])
    expected_files = sorted(
        [
            f"{REJECT_DIR}/testAlbum/240230-anything.mp3",
        ]
    )
    cc = Mp3Tagger()
    cc.run()
    actual_files = get_files()
    assert actual_files == expected_files


def test_mp3_with_3_files(monkeypatch):
    """Test processing of 3 files"""
    shutil.copy2(src=RESOURCE_DIR + "/240229-test1.mp3", dst=DOWNLOAD_DIR + "/240310-test1.mp3")
    shutil.copy2(src=RESOURCE_DIR + "/240229-test1.mp3", dst=DOWNLOAD_DIR + "/240110-test1.mp3")
    shutil.copy2(
        src=RESOURCE_DIR + "/240131-not_a_mp3.mp3", dst=DOWNLOAD_DIR + "/240230-anything.mp3"
    )
    monkeypatch.setattr("sys.argv", ["tagger.py", "-r", "-c", RESOURCE_DIR + "/mp3tagger.ini"])
    expected_files = sorted(
        [
            f"{BACKUP_DIR}/testAlbum/240110-test1.mp3",
            f"{BACKUP_DIR}/testAlbum/240310-test1.mp3",
            f"{MP3_DIR}/testAlbum/240110-test1.mp3",
            f"{MP3_DIR}/testAlbum/240310-test1.mp3",
            f"{REJECT_DIR}/testAlbum/240230-anything.mp3",
        ]
    )
    cc = Mp3Tagger()
    cc.run()
    actual_files = get_files()
    assert actual_files == expected_files


def test_mp3_stderrwith_3_files(capfd, monkeypatch):
    """Test output processing of 3 files"""
    shutil.copy2(src=RESOURCE_DIR + "/240229-test1.mp3", dst=DOWNLOAD_DIR + "/temp.mp3")
    shutil.copy2(src=RESOURCE_DIR + "/240229-test1.mp3", dst=DOWNLOAD_DIR + "/240310-test1.mp3")
    shutil.copy2(src=RESOURCE_DIR + "/240229-test1.mp3", dst=DOWNLOAD_DIR + "/240110-test1.mp3")
    shutil.copy2(
        src=RESOURCE_DIR + "/240131-not_a_mp3.mp3", dst=DOWNLOAD_DIR + "/240230-anything.mp3"
    )
    monkeypatch.setattr("sys.argv", ["tagger.py", "-r", "-c", RESOURCE_DIR + "/mp3tagger.ini"])
    # expected_files = sorted(
    #     [
    #         f"{BACKUP_DIR}/testAlbum/240110-test1.mp3",
    #         f"{BACKUP_DIR}/testAlbum/240310-test1.mp3",
    #         f"{MP3_DIR}/testAlbum/240110-test1.mp3",
    #         f"{MP3_DIR}/testAlbum/240310-test1.mp3",
    #         f"{REJECT_DIR}/testAlbum/240230-anything.mp3",
    #     ]
    # )
    expected_stdout = (
        "Processing file testAlbum/240110-test1.mp3 - OK\n"
        "Processing file testAlbum/240230-anything.mp3\n"
        "    moved to reject ??????????\n"
        "    (Invalid release date: 240230)\n"
        "Processing file testAlbum/240310-test1.mp3 - OK\n"
        "Ignoring temporary file testAlbum/temp.mp3\n"
    )
    cc = Mp3Tagger()
    cc.run()
    out, err = capfd.readouterr()
    # actual_files = get_files()
    assert out == expected_stdout and err == ""
