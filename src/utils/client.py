import datetime
import json
import os
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


def get_task_by_gid(gid: str, session: Session):
    return session.query(Task).filter(Task.id == gid).first()


def add_task_to_store(session: Session, task_gid: str) -> None:
    """Adding task record to Database"""
    task = Task(id=task_gid)
    session.add(task)
    session.commit()


def is_task_completed_today(due_on: str, start_on: str):
    """Return True if due_on(task_completed_deadline equal to today else return False"""
    if start_on is None:
        return due_on == datetime.datetime.today().strftime("%Y-%m-%d")
    return (
        datetime.datetime.strptime(start_on, "%Y-%m-%d")
        < datetime.datetime.today()
        <= datetime.datetime.strptime(f"{due_on} 23:59:59", "%Y-%m-%d %H:%M:%S")
    )


def check_last_polling_session(file_path: str):
    file_exist = os.path.exists(file_path)
    if file_exist:
        with open(file_path, "r") as file:
            try:
                last_check = json.load(file)
            except json.decoder.JSONDecodeError:
                return False

        last_check_date = last_check.get("last_check")
        if last_check_date is not None:
            check_date = last_check_date.split(" ")[0]
            return check_date == datetime.datetime.today().date().strftime("%Y-%m-%d")

        return False

    return False
