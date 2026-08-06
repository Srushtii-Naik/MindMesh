from django.apps import AppConfig


class CommonConfig(AppConfig):
    """
    Shared cross-cutting concerns: auth/permission base classes, pagination,
    exception handling, and other utilities used across domain apps.
    Per ARCHITECTURE.md Section 3.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'
