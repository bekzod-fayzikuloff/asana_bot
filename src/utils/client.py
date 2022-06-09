import datetime
from typing import Generator

from src.db.session import Session
from src.db.tables.task import Task


def is_contain(first_string: str, second_string: str) -> bool:
    """
    Return True if first_arg contain into second_arg else return False
    """
    return first_string in second_string


def is_marked_story(client: dict, story: dict) -> bool:
    """
    Return True if client<gid> and client<name> contain into story<html_text> else return False
    """
    html_text: str = story.get("html_text", "")
    client_gid: str = client.get("gid")
    client_name: str = f'{client.get("name", "")}'

    return all((is_contain(client_gid, html_text), is_contain(client_name, html_text)))


def get_all_tasks_gid(session: Session) -> Generator:
    all_tasks = session.query(Task).all()
    return (task.id for task in all_tasks)


def add_task_to_store(session: Session, task_gid: str) -> None:
    """Adding task record to Database"""
    task = Task(id=task_gid)
    session.add(task)
    session.commit()


def is_task_completed_today(due_on: str):
    """Return True if due_on(task_completed_deadline equal to today else return False"""
    return due_on == datetime.datetime.today().strftime("%Y-%m-%d")
