from apps.existing_database.dataloaders import ExistingDatabaseDataLoader
from django.utils.functional import cached_property


class GobalDataLoader:
    @cached_property
    def existing_database(self):
        return ExistingDatabaseDataLoader()
