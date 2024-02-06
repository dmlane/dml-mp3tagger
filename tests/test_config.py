""" Test config functionality"""

import os

from mp3tagger.config import read_config

# import mock


HOME = os.path.expanduser("~")

EXPECTED_CONFIG_DICT = {
    "backup_dir": "/tmp/mp3_tagger/tests/backup",
    "dest_dir": "/tmp/mp3_tagger/tests/mp3",
    "log_retention_days": "7",
    "reject_dir": "/tmp/mp3_tagger/tests/rejects",
    "source_dir": "/tmp/mp3_tagger/tests/download",
}


def test_config_read_ok():
    """Test config read ok"""
    ini_path = os.path.dirname(os.path.realpath(__file__)) + "/testresources/mp3tagger.ini"
    xx = read_config("mp3tagger", ini_path=ini_path)
    assert xx == EXPECTED_CONFIG_DICT
