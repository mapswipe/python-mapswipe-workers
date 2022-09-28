import time

import schedule
from apps.aggregated.management.commands.update_aggregated_data import (
    Command as AggregateCommand,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, **_):
        AggregateCommand().run()
        schedule.every().day.at("00:10").do(AggregateCommand().run)

        while True:
            # TODO: Upgrade to better scheduler?
            schedule.run_pending()
            time.sleep(60 * 60 * 6)  # Every 6 hours
