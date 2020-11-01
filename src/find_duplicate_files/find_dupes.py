"""
Find duplicate files.
"""
import os
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List

import click
from loguru import logger
from more_itertools import chunked
from tqdm import tqdm


def add_timestamp_to_fn(fn: Path) -> Path:
    """
    Append a timestamp to a filename.
    """
    dtfmt = "%Y%m%d-%H%M%S"

    original_name = fn.stem
    new_name = original_name + "_" + datetime.today().strftime(dtfmt)
    fn = fn.parent / (new_name + fn.suffix)

    return fn


def create_db(db_file: Path) -> None:
    """
    Create the database file.
    """
    # Remember, connection context manager automatically calls "commit()"
    logger.info(f"Creating database file `{db_file}`")
    with sqlite3.connect(str(db_file)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE files (path text, filename text, hash text);
            """
        )
        cursor.execute(
            """
            CREATE TABLE duplicates (path text, filename text, hash text);
            """
        )


def hash_file(filepath: Path) -> str:
    """
    Return the md5 hash of the file.
    """
    args = ["md5sum", str(filepath)]
    # capture_output is python >= 3.7
    #  result = subprocess.run(args, capture_output=True)
    result = subprocess.run(args, stdout=subprocess.PIPE)

    # linux `hashlib` returns "<hash>  <filename>"
    filehash = result.stdout.split(b" ")[0]
    return filehash


def add_all_files(db_file: Path, all_files: List[Path], chunk_size: int = 300) -> None:
    """
    Add all of the files and their hashes to the database.
    """
    logger.debug(f"Hashing and adding to database. Chunk size: {chunk_size}.")

    # Split things into chunks so that we reduce our database I/O.
    # We make the iterator into a list so that tqdm can display true progress.
    for chunk in tqdm(list(chunked(all_files, chunk_size))):
        #  logger.debug(f"Chunk: {chunk[0]}")
        # list of (path, name, hash) tuples
        rows = []
        for filepath in chunk:
            try:
                filehash = hash_file(filepath)
            except Exception:
                filehash = "error"
            filename = filepath.name
            data = (str(filepath), filename, filehash)
            rows.append(data)

        with sqlite3.connect(str(db_file)) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO files(path, filename, hash) values (?, ?, ?)", rows
            )


def walk_files(starting_dir: Path) -> List[Path]:
    """
    Walk over all files.
    """
    logger.info("Collecting files.")
    all_files = []
    for root, dirs, files in os.walk(starting_dir):
        for name in files:
            filepath = Path(root) / name
            logger.trace(f"{filepath}")
            all_files.append(filepath)

    return all_files


def find_dupes(db_file: Path) -> None:
    """
    Find all the duplicates in the database and write them to a new table.
    """
    logger.info("Searching for duplicates.")
    with sqlite3.connect(str(db_file)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                path, filename, hash
            FROM files
            GROUP BY hash
            HAVING COUNT(*) > 1;
            """
        )
        dupes = cursor.fetchall()
        logger.debug(f"Found {len(dupes)} duplicates. Adding to database.")

        cursor.executemany(
            "INSERT INTO duplicates(path, filename, hash) values (?, ?, ?);", dupes
        )


def print_summary(db_file: Path) -> None:
    """
    Print a simple summary to stdout.
    """

    with sqlite3.connect(str(db_file)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files;")
        num_files = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM files WHERE hash = 'error';")
        num_errors = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM duplicates")
        num_dupes = cursor.fetchone()[0]

    logger.info(f"Found {num_files} with {num_errors} errors.")
    logger.info(f"There are {num_dupes} duplicates found.")


@click.command()
@click.option(
    "-o",
    "--outfile",
    default=None,
    type=click.Path(),
    help="File to save data to. If not given, data_<timestamp>.db will be used.",
)
@click.option(
    "--batch-size",
    default=300,
    type=int,
    help=(
        "Batch size for hashing and adding to database. Setting this to a low"
        " value will slow things down by increasing file IO."
    ),
)
@click.argument("path", type=click.Path(exists=True))
def main(path, outfile, batch_size):
    if outfile is None:
        outfile = Path().cwd() / "data.db"
        outfile = add_timestamp_to_fn(outfile)

    create_db(outfile)

    # Pass 1: simply record all of the files.
    all_files = walk_files(path)

    # Pass 2: take the hashes and write to database
    add_all_files(outfile, all_files)

    find_dupes(outfile)

    print_summary(outfile)
    logger.success(f"Completed processing '{outfile}'")


if __name__ == "__main__":
    main()
