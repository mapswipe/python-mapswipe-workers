from collections import defaultdict

from django.apps import apps


class BaseBulkManager(object):
    """
    This helper class keeps track of ORM objects to be action for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is action for all models.
    """

    def __init__(self, chunk_size=100, **commit_kwargs):
        self._queues = defaultdict(list)
        self._commit_kwargs = commit_kwargs
        self.chunk_size = chunk_size

    def _commit(self, _):
        raise Exception("This is not implemented yet.")

    def _process_obj(self, obj):
        return obj

    def add(self, *objs):
        """
        Add an object to the queue to be action, and call bulk_create if we
        have enough objs.
        """
        for obj in objs:
            model_class = type(obj)
            model_key = model_class._meta.label
            self._queues[model_key].append(self._process_obj(obj))
            if len(self._queues[model_key]) >= self.chunk_size:
                self._commit(model_class, **self._commit_kwargs)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self._queues.items():
            if len(objs) > 0:
                self._commit(apps.get_model(model_name))


class BulkCreateManager(BaseBulkManager):
    def _commit(self, model_class, **kwargs):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self._queues[model_key], **kwargs)
        self._queues[model_key] = []
