""" Test config functionality"""

import os
import shutil

from mp3tagger import config

# import mock


HOME = os.path.expanduser("~")
OVERRIDE_DIR = "/tmp/mp3tagger.config"
TEST_CONFIG = os.path.dirname(os.path.realpath(__file__)) + "/testresources/mp3tagger.ini"
OVERRIDE_CONFIG = OVERRIDE_DIR + "/mp3tagger.ini"

EXPECTED_CONFIG_DICT = {
    "backup_dir": "/tmp/mp3_tagger/tests/backup",
    "dest_dir": "/tmp/mp3_tagger/tests/mp3",
    "log_retention_days": "7",
    "reject_dir": "/tmp/mp3_tagger/tests/rejects",
    "source_dir": "/tmp/mp3_tagger/tests/download",
}


def test_config_read_ok():
    """Test config read ok"""
    ini_path = TEST_CONFIG
    xx = config.read_config("mp3tagger", ini_path=ini_path)
    assert xx == EXPECTED_CONFIG_DICT


def test_initial_setup_ok(monkeypatch):
    """Test initial setup ok"""
    shutil.rmtree(OVERRIDE_DIR, ignore_errors=True)
    monkeypatch.setattr(config, "CONFIG_DIR", OVERRIDE_DIR)
    monkeypatch.setattr(config, "CONFIG", OVERRIDE_CONFIG)
    _ = config.read_config("mp3tagger")
    assert os.path.exists(OVERRIDE_DIR + "/mp3tagger.ini")


def test_config_not_overwritten(monkeypatch):
    """Make sure we don't overwrite the config file"""
    shutil.rmtree(OVERRIDE_DIR, ignore_errors=True)
    monkeypatch.setattr(config, "CONFIG_DIR", OVERRIDE_DIR)
    monkeypatch.setattr(config, "CONFIG", OVERRIDE_CONFIG)
    os.makedirs(OVERRIDE_DIR, exist_ok=True)
    shutil.copy(TEST_CONFIG, OVERRIDE_CONFIG)
    _ = config.read_config("mp3tagger")
    with open(OVERRIDE_CONFIG, "r", encoding="ascii") as override_file:
        with open(TEST_CONFIG, "r", encoding="ascii") as test_file:
            assert list(test_file) == list(override_file)
