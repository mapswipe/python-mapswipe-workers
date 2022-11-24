import sentry_sdk
from django.conf import settings
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

IGNORED_ERRORS = []
IGNORED_LOGGERS = [
    "graphql.execution.utils",
]

for _logger in IGNORED_LOGGERS:
    ignore_logger(_logger)


def init_sentry(app_type, tags={}, **config):
    integrations = [
        DjangoIntegration(),
    ]
    sentry_sdk.init(
        **config,
        traces_sample_rate=settings.SENTRY_SAMPLE_RATE,
        ignore_errors=IGNORED_ERRORS,
        integrations=integrations,
    )
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("app_type", app_type)
        for tag, value in tags.items():
            scope.set_tag(tag, value)
