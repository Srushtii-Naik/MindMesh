from django.apps import AppConfig


class AiCompanionConfig(AppConfig):
    """
    ai_companion domain app.

    Scaffolded per ARCHITECTURE.md Section 3 & 9 module boundaries.
    Models, serializers, services, and views are implemented in this app's
    dedicated ROADMAP.md milestone — not part of Project Foundation.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_companion'
