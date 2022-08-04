import datetime
import json
import time

import asana
import schedule

from src import config
from src.resources import email
from src.utils.bot import Bot
from src.utils.client import (
    add_task_to_store,
    check_last_polling_session,
    get_task_by_gid,
    is_marked_story,
    is_task_completed_today,
)
from src.utils.db import get_session, init_db


def main() -> None:
    """
    Script for polling and provide service with Asana API
    """
    client = asana.Client.access_token(config.ACCESS_TOKEN)
    client.headers = {"asana-enable": "new_user_task_lists"}
    bot = Bot(client)

    def schedule_polling() -> None:
        """
        Job which polling in scheduler for observe company workspaces
        """
        session = next(get_session())

        tasks = bot.get_workspaces_tasks()  # getting common workspaces

        for task in tasks:
            # When task already in store(already checked) `skip this loop`
            if get_task_by_gid(gid=str(["gid"]), session=session) is None:
                continue

            task_due_on = task.get("due_on", None)
            start_on = task.get("start_on", None)

            if task_due_on is None:
                try:  # noqa
                    assigner = bot.get_task_assignee(task["gid"])["assignee"].copy()
                    bot.change_task_state(task)
                    message = email.make_story_hmtl(assigner, email.EXPIRED_TEXT)
                    bot.create_story_on_task(task_gid=task["gid"], message=message)
                    bot.move_section(task)
                finally:
                    continue

            if not is_task_completed_today(task_due_on, start_on):
                if check_last_polling_session("last_check.json"):
                    try:  # noqa
                        assigner = bot.get_task_assignee(task["gid"])["assignee"].copy()
                        bot.change_task_state(task)
                        message = email.make_story_hmtl(assigner, email.EXPIRED_TEXT)
                        bot.create_story_on_task(task_gid=task["gid"], message=message)
                        bot.move_section(task)
                    finally:
                        continue

            stories = bot.get_task_stories(task["gid"])  # Getting all stories from has not been verified task

            for story in stories:
                if is_marked_story(bot.me, story):  # Skip all stories from task when story contains `@bot_name`
                    add_task_to_store(session, task["gid"])
                    break
            else:  # Else mark task as uncompleted and add templated story(comment)
                try:
                    assigner = bot.get_task_assignee(task["gid"])["assignee"].copy()  # if assigner is None skip loop
                except AttributeError:
                    continue

                bot.change_task_state(task)
                message = email.make_story_hmtl(assigner, email.DEFAULT_TEXT)
                bot.move_section(task)
                bot.create_story_on_task(task_gid=task["gid"], message=message)

        with open("last_check.json", "w+") as file:
            file.write(json.dumps({"last_check": datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")}))

        session.close()

    schedule_polling()

    schedule.every(4).minutes.do(schedule_polling)  # run `job` every 4 minutes
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:  # noqa
            pass


if __name__ == "__main__":
    """Start main function if this module will not import"""
    init_db()
    main()
