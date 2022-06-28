from django.utils.functional import cached_property
from apps.existing_database.dataloaders import ExistingDatabaseDataLoader


class GobalDataLoader():
    @cached_property
    def existing_database(self):
        return ExistingDatabaseDataLoader()
