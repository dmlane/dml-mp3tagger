""" Change mp3 tags to what I need"""

import argparse
import glob
import os.path
import sys
from importlib.metadata import version

from mp3tagger._util import (
    MyData,
    MyException,
    RawFormatter,
    move_to_final,
    move_to_reject,
    save_original_file,
)
from mp3tagger.config import read_config
from mp3tagger.id3handler import ID3Handler

LINE_LENGTH = 90


class Mp3Tagger:
    """Change mp3 tags to what I need"""

    backup_dir = None
    config_file = None
    dest_dir = None
    log_retention_days = 7
    parser = None
    reject_dir = None
    remove_source_file = False
    source_dir = None
    verbose = False

    def make_cmd_line_parser(self):
        """Set up the command line parser"""
        self.parser = argparse.ArgumentParser(
            formatter_class=RawFormatter,
            description="Re-tag mp3 to match what we need in Apple Music",
        )
        self.parser.add_argument(
            "-V",
            "--version",
            action="version",
            version=version("dml-mp3tagger"),
            help="Print the version number",
        )
        self.parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            default=False,
            help="Verbose output",
        )
        self.parser.add_argument(
            "-r",
            "--remove-source_file",
            action="store_true",
            default=False,
            help="Remove the source file after processing",
        )
        self.parser.add_argument(
            "-c",
            "--config_file",
            default=None,
            help="Configuration file to use",
        )

    def parse_args(self):
        """Parse the command line arguments"""
        args = self.parser.parse_args()

        self.verbose = args.verbose
        self.remove_source_file = args.remove_source_file
        self.config_file = args.config_file

    def read_config(self):
        """Read the config file"""
        config = read_config("mp3tagger", ini_path=self.config_file)

        self.log_retention_days = int(config["log_retention_days"])
        self.source_dir = config["source_dir"]
        self.dest_dir = config["dest_dir"]
        self.backup_dir = config["backup_dir"]
        self.reject_dir = config["reject_dir"]

    def validate_config(self):
        """Validate the config file"""
        if not os.path.isdir(self.source_dir):
            raise FileNotFoundError(self.source_dir)
        if not os.path.isdir(self.dest_dir):
            raise FileNotFoundError(self.dest_dir)
        if not os.path.isdir(self.backup_dir):
            raise FileNotFoundError(self.backup_dir)
        if not os.path.isdir(self.reject_dir):
            raise FileNotFoundError(self.reject_dir)

    def process_file(self, full_file_name):
        """Process current file"""
        parts = full_file_name.split("/")
        short_name = parts[-2] + "/" + parts[-1]
        if len(short_name) > LINE_LENGTH:
            short_name = short_name[: LINE_LENGTH - 4] + "...."
        if "/temp.mp3" in full_file_name:
            # Ignore temporary files
            print(
                f"Ignoring temporary file {short_name}",
            )
            return 1
        print(f"Processing file {short_name}", end="")
        md = MyData(
            input_file=full_file_name,
            dest_dir=self.dest_dir,
            backup_dir=self.backup_dir,
            reject_dir=self.reject_dir,
        )
        try:
            id3 = ID3Handler()
            id3.process_podcast(md)

            move_to_final(md)

            if self.remove_source_file:
                save_original_file(md)
        except Exception as inst:
            print("\n    moved to reject ??????????")
            move_to_reject(md)
            raise inst
        print(" - OK")
        return 0

    def process_all_files(self):
        """Process all files in the source directory"""

        all_files = sorted(glob.glob(f"{self.source_dir}/*/*.mp3"))
        if len(all_files) == 0:
            print(f"No files found in {self.source_dir}")
            return 0
        bad_files = 0
        bad_list = []
        good_files = 0
        for file_name in all_files:
            try:
                self.process_file(file_name)
                good_files += 1
            except MyException as inst:
                msg = inst.msg
                print(f"    ({msg})")
                bad_files += 1
                bad_list.append(file_name)
        print(f"Processed {good_files} good files", end=" ")
        if bad_files > 0:
            print(f"{bad_files} bad files.")
            print("Bad files:")
            for file_name in bad_list:
                print(f"    {file_name}")
        print("\nEnd of run ++++++++++")
        return 0

    def run(self):
        """Main entry point"""

        self.make_cmd_line_parser()
        self.parse_args()
        self.read_config()
        self.validate_config()
        self.process_all_files()


def main():
    """Main entry point"""
    try:
        Mp3Tagger().run()
    except MyException as e:
        print(e.msg)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"File/directory not found: '{e}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
