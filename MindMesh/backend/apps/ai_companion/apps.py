from django.apps import AppConfig


class AiCompanionConfig(AppConfig):
    """
    ai_companion domain app.

    The AI Provider Abstraction Layer (providers.py, services.py) was
    brought forward minimally in Milestone 6 to power Notes' AI summaries.
    Milestone 7 (ROADMAP.md) completes the conversational surface described
    in ARCHITECTURE.md Section 7: conversations, chat messages, the Context
    Assembly Service, foundational memory extraction, and AI-enhanced
    suggestions. The full long-term memory engine (recall, dedup/
    categorization, embeddings/RAG-readiness) is Milestone 8 scope.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_companion'
