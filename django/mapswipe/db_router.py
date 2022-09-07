from django.conf import settings


class DatabaseRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """

    CURRENT_DB = settings.MAPSWIPE_EXISTING_DB

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label == self.CURRENT_DB:
            return self.CURRENT_DB
        return "default"

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label == self.CURRENT_DB:
            return self.CURRENT_DB
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return "default"
