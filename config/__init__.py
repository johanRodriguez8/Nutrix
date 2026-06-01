"""Centralized application configuration.

Single source of truth for every deployment/environment value
(robot IPs, ports, OPC UA URLs, SSH credentials, shared paths, admin
password). Import the ready-to-use singleton:

    from config import settings
    ip = settings.ip1
"""
from config.settings import settings, Settings

__all__ = ["settings", "Settings"]
