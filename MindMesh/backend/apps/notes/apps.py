from django.apps import AppConfig


class NotesConfig(AppConfig):
    """
    notes domain app.

    Implements ROADMAP.md Milestone 6 (Notes & Knowledge): categories, tags,
    rich notes, attachments, search, and AI summaries (via the AI
    abstraction layer in apps.ai_companion). Follows the layering in
    ARCHITECTURE.md Section 3.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notes'
