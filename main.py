import datetime
import json
import time

import asana
import schedule

from src import config
from src.db.session import Session
from src.services.skan import ScanService
from src.utils.bot import Bot
from src.utils.db import init_db


def main() -> None:
    """
    Script for polling and provide service with Asana API
    """
    client = asana.Client.access_token(config.ACCESS_TOKEN)
    client.headers = {"asana-enable": "new_user_task_lists"}
    bot = Bot(client)
    service = ScanService(pool=Session, client=bot)

    def schedule_polling() -> None:
        """
        Job which polling in scheduler for observe company workspaces
        """
        service.start_scan()

        with open("last_check.json", "w+") as file:
            file.write(json.dumps({"last_check": datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")}))

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
