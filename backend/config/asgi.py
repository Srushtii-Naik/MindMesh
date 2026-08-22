"""ASGI config for MindMesh.

Present for forward-compatibility with the real-time/streaming upgrade path
noted in ARCHITECTURE.md Section 6 (WebSockets/SSE), not required at this stage.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_asgi_application()
