from django.apps import AppConfig


class FamilyConfig(AppConfig):
    """
    family domain app.

    Implements ROADMAP.md Milestone 10 — Family & Shared Workspace: member
    invitation/management, shared tasks/calendar/notes, and emergency
    contacts, per ARCHITECTURE.md Section 3 & 9 module boundaries.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.family'
