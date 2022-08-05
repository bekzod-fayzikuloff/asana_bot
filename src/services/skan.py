from sqlalchemy.orm import Session, sessionmaker

from src.resources import email
from src.utils.bot import Bot
from src.utils.client import (
    add_task_to_store,
    check_last_polling_session,
    get_task_by_gid,
    is_marked_story,
    is_task_completed_today,
)


class ScanService:
    def __init__(self, pool: sessionmaker, client: Bot):
        self.pool = pool
        self.client = client

    def start_scan(self):
        with self.pool() as session:
            self.polling(session)

    def polling(self, session=Session):
        tasks = self.client.get_workspaces_tasks()  # getting common workspaces

        for task in tasks:
            # When task already in store(already checked) `skip this loop`
            if get_task_by_gid(gid=str(task["gid"]), session=session) is None:
                continue

            task_due_on = task.get("due_on")
            start_on = task.get("start_on")

            if task_due_on is None:
                try:
                    assigner = self.client.get_task_assignee(task["gid"])["assignee"].copy()
                    message = email.make_story_hmtl(assigner, email.EXPIRED_TEXT)

                    self.unmark_task(task, message)
                finally:
                    continue

            if not is_task_completed_today(task_due_on, start_on):
                if check_last_polling_session("last_check.json"):
                    try:
                        assigner = self.client.get_task_assignee(task["gid"])["assignee"].copy()
                        message = email.make_story_hmtl(assigner, email.EXPIRED_TEXT)

                        self.unmark_task(task, message)
                    finally:
                        continue

            stories = self.client.get_task_stories(task["gid"])  # Getting all stories from has not been verified task

            for story in stories:
                if is_marked_story(self.client.me, story):  # Skip all stories from task when story contains `@bot_name`
                    add_task_to_store(session, task["gid"])
                    break
            else:  # Else mark task as uncompleted and add templated story(comment)
                try:
                    # if assigner is None skip loop
                    assigner = self.client.get_task_assignee(task["gid"])["assignee"].copy()
                except AttributeError:
                    continue

                message = email.make_story_hmtl(assigner, email.DEFAULT_TEXT)
                self.unmark_task(task, message)

    def unmark_task(self, task: dict, message: str) -> None:
        self.client.change_task_state(task)
        self.client.move_section(task)
        self.client.create_story_on_task(task_gid=task["gid"], message=message)
