import pytest
import pathlib

import dateparser

from trashbot.parsers.parser import Parser

TEST_PHRASE_PATH = pathlib.Path("input_phrases/phrases.yml")


@pytest.fixture
def parser():
    parser = Parser()
    parser.initialize(
        phrase_file_path=TEST_PHRASE_PATH,
        database_file_path=":memory:",
    )
    yield parser
    parser.close()


def test_phrase(parser):
    time_check = dateparser.parse("10:00am", settings={"TIMEZONE": "PST"})
    phrase = "set a reminder for 10:00am to walk the dog"
    parser.determine_intent(phrase)
    assert len(parser._manager._reminders) == 1
    for val in parser._manager._reminders.values():
        assert val.id != 0
        assert val.reminder == "walk the dog"
        assert val.notification_time == time_check


def test_phrase_too(parser):
    time_check = dateparser.parse("10:00am", settings={"TIMEZONE": "PST"})
    phrase = "reminder me at 10:00am to walk the dog"
    parser.determine_intent(phrase)
    assert len(parser._manager._reminders) == 1
    for val in parser._manager._reminders.values():
        assert val.id != 0
        assert val.reminder == "walk the dog"
        assert val.notification_time == time_check


def test_phrase_three(parser):
    time_check = dateparser.parse("November 18 10:00am", settings={"TIMEZONE": "PST"})
    phrase = "add a reminder at 10:00am on November 18 to send a card"
    parser.determine_intent(phrase)
    assert len(parser._manager._reminders) == 1
    for val in parser._manager._reminders.values():
        assert val.id != 0
        assert val.reminder == "send a card"
        assert val.notification_time == time_check


def test_phrase_four(parser):
    time_check = dateparser.parse("tomorrow 10:00am", settings={"TIMEZONE": "PST"})
    phrase = "add a reminder at 10:00am tomorrow to send a card"
    parser.determine_intent(phrase)
    assert len(parser._manager._reminders) == 1
    for val in parser._manager._reminders.values():
        assert val.id != 0
        assert val.reminder == "send a card"
        assert val.notification_time == time_check


def test_phrase_five(parser):
    # TODO: Add a more dynamic test
    time_check = dateparser.parse(
        "January 1, 2023 10:00am", settings={"TIMEZONE": "PST"}
    )
    phrase = "add a reminder for 10:00am on January 1 to send a card"
    parser.determine_intent(phrase)
    assert len(parser._manager._reminders) == 1
    for val in parser._manager._reminders.values():
        assert val.id != 0
        assert val.reminder == "send a card"
        assert val.notification_time == time_check


def test_phrase_six(parser):
    phrase = "add a timer for 1 hour"
    parser.determine_intent(phrase)


def test_phrase_seven(parser):
    phrase = "add a timer for 10 hours"
    parser.determine_intent(phrase)


def test_phrase_eight(parser):
    phrase = "add a timer for 1 minute"
    parser.determine_intent(phrase)


def test_phrase_nine(parser):
    phrase = "add a timer for 30 minutes"
    parser.determine_intent(phrase)


def test_phrase_ten(parser):
    phrase = "add a timer for 45 seconds"
    parser.determine_intent(phrase)


def test_phrase_eleven(parser):
    phrase = "add a timer for 10 second"
    parser.determine_intent(phrase)
