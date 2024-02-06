""" Read config file"""

import os
import shutil
from configparser import BasicInterpolation, ConfigParser

import appdirs

# Config file provided as part of the package
DEFAULT_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "data", "mp3tagger.ini"
)

# Local config which will override the default config file
CONFIG_DIR = appdirs.user_config_dir("net.dmlane")
CONFIG = os.path.join(CONFIG_DIR, "mp3tagger.ini")

# These will be used by ConfigParser to expand variables in the ini file
VARS = {
    # "BLANK": "blank",
}


class EnvInterpolation(BasicInterpolation):  # pylint: disable=too-few-public-methods
    """Interpolation which expands environment variables in values."""

    def before_get(
        self, parser, section, option, value, defaults
    ):  # pylint: disable=too-many-arguments
        """Expand environment variables in values"""
        value = super().before_get(parser, section, option, value, defaults)

        return os.path.expanduser(value)


def read_config(section, ini_path=None):
    """Read config file - returning a dictionary of config values from section"""
    if ini_path is None:
        configs_to_read = [DEFAULT_CONFIG_FILE, CONFIG]
    else:
        configs_to_read = [ini_path]
    # If config not in correct location, create it from the default ini file
    ini_path = ini_path or CONFIG
    if not os.path.exists(ini_path):
        if ini_path is None:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            shutil.copy(DEFAULT_CONFIG_FILE, CONFIG)
        else:
            raise FileNotFoundError(ini_path)
    config = ConfigParser(
        interpolation=EnvInterpolation(),
        defaults=VARS,
    )
    # We need to read the default config file first in case sections or fields have been
    # added to the default config file.
    # The 2nd file overrides the 1st one
    config.read(configs_to_read)
    return dict(config[section])
