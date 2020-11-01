# Duplicate File Finder

A very simple script that finds all duplicate files (via md5 checksum) and
saves the results to an sqlite3 database file.


## Usage

```
find_dupes --help

find_dupes -o some_db_file.db /path/to/search

find_dupes --batch-size 1000 /path/to/search
```


### SQLite3 File

The sqlite3 file that is generated has two tables: `files` and `duplicates`.
The `files` table stores the md5sum, file path, and file name of every file
the program parsed and the `duplicates` table records the same values but only
if two or more files have the same md5 checksum.


## Installation

1. Make a virtal environment
2. Install requirements: `pip install -r requirements.txt`
3. Install the package: `pip install -e .`
