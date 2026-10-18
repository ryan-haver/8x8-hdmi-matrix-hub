"""8x8 HDMI Matrix Hub.

The consolidated hub package (Phase 4, WP-C3). ``hub.core`` holds the single
owner of matrix state (:class:`hub.core.MatrixService`), the port/capability
model (:class:`hub.core.MatrixModel`), the name store and the event bus that
REST, WebSocket and the integrations subscribe to.
"""

__version__ = "1.0.0rc1"
