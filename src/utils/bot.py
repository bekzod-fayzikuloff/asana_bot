import itertools
from itertools import chain

from asana.page_iterator import PageIterator


class Bot:
    def __init__(self, client) -> None:
        self.client = client

    def get_workspaces(self) -> dict:
        """
        Getting dict with user_gid and user workspaces data
        """
        return self.client.users.me(opt_fields="workspaces")

    def get_workspaces_tasks(self) -> chain[PageIterator]:
        """
        Get all referenced `to self.client.users.me()` completed tasks from all workspaces
        """
        workspaces = tuple(self.get_workspaces()["workspaces"])
        tasks_lists = []

        for workspace in workspaces:
            workspace_task = self.client.tasks.search_tasks_for_workspace(
                workspace_gid=workspace["gid"],
                completed=True,
                params={"followers.any": self.me["gid"]},
                opt_fields=["name", "due_on", "memberships.project"],
            )
            tasks_lists.append(workspace_task)

        return itertools.chain(*tuple(tasks_lists))

    def get_task_assignee(self, task_gid) -> dict:
        return self.client.tasks.get_task(task_gid, opt_fields=["assignee", "assignee.name"])

    def get_task_stories(self, task_gid: str) -> PageIterator:
        """
        Getting all stories from task
        """
        return self.client.stories.get_stories_for_task(task_gid=task_gid, opt_fields=["html_text"])

    def change_task_state(self, task: dict) -> None:
        """
        Send response to API `PUT /tasks/{task_gid}`
        for changing state to not completed
        """
        self.client.tasks.update_task(task["gid"], {"completed": False})

    def create_story_on_task(self, task_gid: str, message: str) -> None:
        """
        Creating story on task with message in case when `assigner` miss mark `bot` in comments
        with templated text
        """

        self.client.stories.create_story_for_task(task_gid, {"html_text": message})

    def move_section(self, task: dict) -> None:
        """
        Move task to `in processing` section
        """
        try:
            sections = self.client.sections.get_sections_for_project(task["memberships"][0]["project"]["gid"])
        except TypeError:
            return

        in_processing = None
        for section in sections:
            if section["name"].lower() == "повторная обработка":
                in_processing = section["gid"]

        if in_processing is not None:
            self.client.sections.add_task_for_section(in_processing, {"task": task["gid"]})

    @property
    def me(self) -> dict:
        """
        Property for getting info about client user
        """
        return self.client.users.me()
