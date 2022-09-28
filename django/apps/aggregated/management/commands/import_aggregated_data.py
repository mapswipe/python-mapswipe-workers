import csv
from sys import stdin
from argparse import FileType

from django.core.management.base import BaseCommand
from django.db import models

from apps.aggregated.models import AggregatedUserStatData
from mapswipe.managers import BulkCreateManager

DEFAULT_CHUNK_SIZE = 100000


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'input_file_stream',
            nargs='?',
            type=FileType('r'),
            default=stdin,
            help=(
                'CSV file exported from '
                'aggregated_project_user_timestamp_data materialized view'
            ),
        )
        parser.add_argument(
            '--chunk-size',
            action='store',
            type=int,
            default=DEFAULT_CHUNK_SIZE,
            help=(
                'Size by which bulk insert/update are send to database. '
                f'Default: {DEFAULT_CHUNK_SIZE}'
            ),
        )

    def handle(self, **options):
        input_file = options['input_file_stream']
        reader = csv.DictReader(input_file)
        chunk_size = options['chunk_size']
        manager = BulkCreateManager(
            chunk_size=chunk_size,
            update_conflicts=True,
            unique_fields=('project_id', 'user_id', 'timestamp_date',),
            update_fields=('total_time', 'task_count', 'area_swiped',)
        )
        self.stdout.write('Processing input')
        for index, row in enumerate(reader, start=1):
            print(f'- Saving: {index}', end='\r')
            manager.add(
                AggregatedUserStatData(
                    project_id=row['project_id'],
                    user_id=row['user_id'],
                    timestamp_date=row['timestamp_date'],
                    total_time=int(float(row['total_time'] or 0)),
                    task_count=row['task_count'],
                    area_swiped=row['area_swiped'],
                    swipes=0,  # Will calculate this later
                )
            )
        self.stdout.write('Post-processing...')
        # Re-calcuate data for swipes using project_type
        AggregatedUserStatData.objects.exclude(project__project_type=1)\
            .update(swipes=models.F('task_count'))
        AggregatedUserStatData.objects\
            .filter(project__project_type=1)\
            .update(swipes=models.F('task_count') / 6)
        self.stdout.write(self.style.SUCCESS('Successfully imported'))
