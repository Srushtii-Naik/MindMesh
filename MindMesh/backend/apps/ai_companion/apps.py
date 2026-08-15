from django.apps import AppConfig


class AiCompanionConfig(AppConfig):
    """
    ai_companion domain app.

    Scaffolded per ARCHITECTURE.md Section 3 & 9 module boundaries. The AI
    Provider Abstraction Layer (providers.py, services.py) is brought
    forward minimally in ROADMAP.md Milestone 6 (Notes & Knowledge) to
    power AI summaries, per that milestone's completion checklist. The full
    conversational surface — models, serializers, views, chat endpoints,
    context assembly, and memory extraction — is implemented in Milestones
    7 and 8.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_companion'
