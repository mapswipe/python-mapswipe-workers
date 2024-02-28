import copy
import os
import typing

from django.db import models


class InvalidGitRepository(Exception):
    pass


def fetch_git_sha(path, head=None):
    """
    Source:
    https://github.com/getsentry/raven-python/blob/03559bb05fd963e2be96372ae89fb0bce751d26d/raven/versioning.py
    >>> fetch_git_sha(os.path.dirname(__file__))
    """
    if not head:
        head_path = os.path.join(path, ".git", "HEAD")
        if not os.path.exists(head_path):
            raise InvalidGitRepository(
                "Cannot identify HEAD for git repository at %s" % (path,)
            )

        with open(head_path, "r") as fp:
            head = str(fp.read()).strip()

        if head.startswith("ref: "):
            head = head[5:]
            revision_file = os.path.join(path, ".git", *head.split("/"))
        else:
            return head
    else:
        revision_file = os.path.join(path, ".git", "refs", "heads", head)

    if not os.path.exists(revision_file):
        if not os.path.exists(os.path.join(path, ".git")):
            raise InvalidGitRepository(
                "%s does not seem to be the root of a git repository" % (path,)
            )

        # Check for our .git/packed-refs' file since a `git gc` may have run
        # https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery
        packed_file = os.path.join(path, ".git", "packed-refs")
        if os.path.exists(packed_file):
            with open(packed_file) as fh:
                for line in fh:
                    line = line.rstrip()
                    if line and line[:1] not in ("#", "^"):
                        try:
                            revision, ref = line.split(" ", 1)
                        except ValueError:
                            continue
                        if ref == head:
                            return str(revision)

        raise InvalidGitRepository(
            'Unable to find ref to head "%s" in repository' % (head,)
        )

    with open(revision_file) as fh:
        return str(fh.read()).strip()


def raise_if_field_not_found(obj: dict, fields: list[str], custom_exception=Exception):
    """
    NOTE: This is for making sure dev pass this variables manually in the test.
    Don't catch this exception
    """
    empty_keys = [field for field in fields if obj.get(field) is None]
    if empty_keys:
        raise custom_exception(f"Please define this fields {empty_keys}")


def get_queryset_for_model(
    model: typing.Type[models.Model],
    queryset: models.QuerySet | None = None,
) -> models.QuerySet:
    if queryset is not None:
        return copy.deepcopy(queryset)
    return model.objects.all()
