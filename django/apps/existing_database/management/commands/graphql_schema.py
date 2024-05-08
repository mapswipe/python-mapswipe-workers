import argparse

from django.core.management.base import BaseCommand
from mapswipe.graphql import schema
from strawberry.printer import print_schema


class Command(BaseCommand):
    help = "Create schema.graphql file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--out",
            type=argparse.FileType("w"),
            default="schema.graphql",
        )

    def handle(self, *args, **options):
        file = options["out"]
        file.write(print_schema(schema))
        file.close()
        self.stdout.write(self.style.SUCCESS(f"{file.name} file generated"))
