from __future__ import annotations

import pathlib

import click

from ..parsers.parser import Parser
from ..managers.database import DatabaseManager


@click.command()
@click.argument("input", type=str)
@click.option(
    "-p", "--phrase-file", "phrases_file_path", type=pathlib.Path, required=True
)
@click.option(
    "-d", "--database-file", "database_file_path", type=pathlib.Path, required=True
)
def test_parsing(
    input, phrases_file_path: pathlib.Path, database_file_path: pathlib.Path
):
    parser = Parser()
    try:
        parser.initialize(
            phrase_file_path=phrases_file_path, database_file_path=database_file_path
        )
        parser.determine_intent(input)
    finally:
        parser.close()


@click.command()
@click.argument("database_file_path", type=pathlib.Path)
def create_reminder_table(database_file_path: pathlib.Path):
    dbm = DatabaseManager(database_file_path)
    try:
        dbm.create_reminder_table()
    finally:
        dbm.close_db()
