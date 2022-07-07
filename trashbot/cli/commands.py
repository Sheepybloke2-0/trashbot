from __future__ import annotations

import pathlib
import sqlite3

import click

from ..parsers.reminder_parser import ReminderParser


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
    parser = ReminderParser()
    parser.initialize(
        phrase_file_path=phrases_file_path, database_file_path=database_file_path
    )
    parser.determine_intent(input)


@click.command()
@click.argument("database_file_path", type=pathlib.Path)
def create_reminder_table(database_file_path: pathlib.Path):
    query = """
        CREATE TABLE IF NOT EXISTS reminders (
            id TEXT PRIMARY KEY,
            reminder TEXT NOT NULL,
            notification_time TEXT NOT NULL
        );
    """
    conn = sqlite3.connect(database_file_path)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.close()
