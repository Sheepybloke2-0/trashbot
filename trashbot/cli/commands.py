from __future__ import annotations

import pathlib

import click

from ..parsers.reminder_parser import ReminderParser


@click.command()
@click.argument("input", type=str)
@click.option(
    "-p", "--phrase-file", "phrases_file_path", type=pathlib.Path, required=True
)
def test_parsing(input, phrases_file_path: pathlib.Path):
    parser = ReminderParser()
    parser.initialize(phrase_file_path=phrases_file_path)
    parser.determine_intent(input)


if __name__ == "__main__":
    test_parsing()
