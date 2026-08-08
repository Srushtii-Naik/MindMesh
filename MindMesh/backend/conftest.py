"""
Root pytest configuration.

Database, email backend, Celery eager mode, and OAuth client ID are all
fixed in config/settings/test.py (see pytest.ini) rather than here, so the
test environment is deterministic regardless of import ordering.
"""
