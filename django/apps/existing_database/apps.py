from django.apps import AppConfig


class ExistingDatabaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.existing_database"
