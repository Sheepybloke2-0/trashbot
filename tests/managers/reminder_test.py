import pytest
import datetime
import pathlib
import yaml

from trashbot.managers.reminder import ReminderManager
from trashbot.managers.database import DatabaseManager

TEST_PHRASE_PATH = pathlib.Path("input_phrases/phrases.yml")


@pytest.fixture
def dbm():
    dbm = DatabaseManager(":memory:")
    yield dbm
    dbm.close_db()


@pytest.fixture
def setup_db(dbm):
    dbm.create_reminder_table()
    with dbm._db_conn:
        dbm._db_conn.execute(
            """
            INSERT INTO reminders
            (id, reminder, notification_time)
            VALUES ('1234567890', 'jump the shark', '2022-07-08T09:00');
            """
        )
    yield dbm


@pytest.fixture
def manager_full(setup_db):
    with open(TEST_PHRASE_PATH, "r") as file:
        phrases = yaml.safe_load(file)
        actions = phrases["adapt_phrases"]["reminders"]["actions"]

    manager = ReminderManager(actions, setup_db)
    yield manager


@pytest.fixture
def manager_empty(dbm):
    with open(TEST_PHRASE_PATH, "r") as file:
        phrases = yaml.safe_load(file)
        actions = phrases["adapt_phrases"]["reminders"]["actions"]

    manager = ReminderManager(actions, dbm)
    yield manager


def test_init_reminders(manager_full):
    manager_full.init_reminders()
    assert manager_full._reminders.get(1234567890) is not None
    assert manager_full._reminders[1234567890].id == 1234567890
    assert manager_full._reminders[1234567890].reminder == "jump the shark"
    assert manager_full._reminders[
        1234567890
    ].notification_time == datetime.datetime.fromisoformat("2022-07-08T09:00")


def test_create_table(manager_empty):
    manager_empty.init_reminders()
    with manager_empty._dbm._db_conn:
        cursor = manager_empty._dbm._db_conn.execute(
            """
            SELECT count(name) FROM sqlite_master 
            WHERE type='table' AND name='reminders'
            """
        )
        assert cursor.fetchone()[0] == 1


def test_create_reminder(manager_full):
    # TODO: Might add later, but more bang for buck at the parser level.
    pass
