from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """
    analytics domain app.

    Implements ROADMAP.md Milestone 11 — Analytics & Insights: productivity
    analytics, habit tracking, AI-generated recommendations (via the AI
    abstraction layer), and weekly progress reports, per ARCHITECTURE.md
    Section 3 & 9 module boundaries.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analytics'
