import pytest

import datetime

from trashbot.managers.database import DatabaseManager
from trashbot.types.reminders import Reminder


@pytest.fixture
def manager():
    manager = DatabaseManager(":memory:")
    manager.create_reminder_table()
    yield manager
    manager.close_db()


@pytest.fixture
def setup_db(manager):
    with manager._db_conn:
        manager._db_conn.execute(
            """
            INSERT INTO reminders
            (id, reminder, notification_time)
            VALUES ('1234567890', 'jump the shark', '2022-07-08T09:00');
            """
        )
    yield manager


def test_db_setup():
    manager = DatabaseManager(":memory:")
    assert manager._db_conn is not None
    assert manager._db_path == ":memory:"
    manager.close_db()


def test_create_table():
    manager = DatabaseManager(":memory:")
    manager.create_reminder_table()
    cursor = manager._db_conn.execute("SELECT * FROM reminders")
    names = [description[0] for description in cursor.description]
    assert "id" in names
    assert "reminder" in names
    assert "notification_time" in names


def test_insert_reminder(manager):
    reminder = Reminder(
        id=1234567890,
        reminder="jump the shark",
        notification_time=datetime.datetime.fromisoformat("2022-07-08T09:00"),
    )
    manager.insert_reminder(reminder)
    reminders = []
    with manager._db_conn:
        for row in manager._db_conn.execute("SELECT * FROM reminders;"):
            reminders.append(
                Reminder(
                    id=int(row[0]),
                    reminder=row[1],
                    notification_time=datetime.datetime.fromisoformat(row[2]),
                )
            )
    assert len(reminders) == 1
    assert reminders[0].id == reminder.id
    assert reminders[0].reminder == reminder.reminder
    assert reminders[0].notification_time == reminder.notification_time


def test_get_reminders(setup_db):
    reminders = setup_db.get_reminders()
    assert len(reminders) == 1
    assert reminders[0].id == 1234567890
    assert reminders[0].reminder == "jump the shark"
    assert reminders[0].notification_time == datetime.datetime.fromisoformat(
        "2022-07-08T09:00"
    )
