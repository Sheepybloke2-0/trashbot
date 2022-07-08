import pytest
import pathlib

from trashbot.parsers.reminder_parser import ReminderParser

TEST_PHRASE_PATH = pathlib.Path("input_phrases/phrases.yml")


@pytest.fixture
def parser():
    parser = ReminderParser()
    parser.initialize(
        phrase_file_path=TEST_PHRASE_PATH,
        database_file_path=":memory:",
    )

    parser.close()
