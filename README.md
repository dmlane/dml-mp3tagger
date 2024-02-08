# dml-mp3tagger

Processes the podcasts downloaded by greg. 
	- Files are rejected if they are not valid mp3 files.
	- If files are rejected, run them through ffmpeg to see if they are fixed.
	- Modify metdadata id3 tags using mutagen
		- Strip out characters which cause problems in the title
		- Change the album name to match the folder it's in
		- Mark it as a podcast
	- Saves the result in the mp3 folder.
	- Saves the original file in the backup folder where it's held for X days.

## Installation
	- Install from my pypi library on fury.io

## Usage

usage: mp3tagger [-h] [-V] [-v] [-r] [-c CONFIG_FILE]

Re-tag mp3 to match what we need in Apple Music

options:
  -h, --help            show this help message and exit
  -V, --version         Print the version number
  -v, --verbose         Verbose output
  -r, --remove-source_file
                        Remove the source file after processing
  -c CONFIG_FILE, --config_file CONFIG_FILE
                        Configuration file to use
