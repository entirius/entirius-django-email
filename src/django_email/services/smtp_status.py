# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Per-channel SMTP state for UIs and checks — bounded, cached, never raises.

``smtp_status`` reads settings only. ``smtp_probe`` logs in to the server, so it runs only on an explicit
request (a login on every screen load looks like a bot to Gmail/M365).
"""

import contextlib
import logging
from enum import StrEnum
from smtplib import SMTPAuthenticationError

from django.core.cache import cache
from django.core.mail import get_connection

from django_email import settings

logger = logging.getLogger(__name__)

REQUIRED_KEYS = ("EMAIL_HOST", "EMAIL_PORT", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD", "EMAIL_USE_SSL", "EMAIL_USE_TLS")
# Present is not enough for these: an unset env var arrives as "" and would pass a presence test. User and
# password may be empty on purpose (unauthenticated relay), the two flags are legitimately False.
NON_EMPTY_KEYS = ("EMAIL_HOST", "EMAIL_PORT")
CACHE_KEY = "django_email.smtp_probe:{idx}"
CACHE_TTL_S = 60
PROBE_TIMEOUT_S = 5


class SmtpStatus(StrEnum):
    CONFIGURED = "configured"
    UNCONFIGURED = "unconfigured"
    UNREACHABLE = "unreachable"
    AUTH_FAILED = "auth_failed"


def channel_entries() -> dict:
    """``EMAIL_SMTP_CONFIGURATION_CHANNELS`` as a dict (the setting defaults to ``None``)."""
    return settings.EMAIL_SMTP_CONFIGURATION_CHANNELS or {}


def missing_keys(channel_idx: str) -> list[str]:
    """Keys the channel's entry lacks, or leaves empty where a value is required."""
    entry = channel_entries().get(channel_idx) or {}
    return [key for key in REQUIRED_KEYS if key not in entry or (key in NON_EMPTY_KEYS and not entry[key])]


def smtp_status(channel_idx: str) -> SmtpStatus:
    """``configured`` when the channel has a complete entry; no network."""
    if channel_idx not in channel_entries() or missing_keys(channel_idx):
        return SmtpStatus.UNCONFIGURED
    return SmtpStatus.CONFIGURED


def smtp_probe(channel_idx: str) -> SmtpStatus:
    """``smtp_status`` plus one cached SMTP login when the entry is complete."""
    configured = smtp_status(channel_idx)
    if configured != SmtpStatus.CONFIGURED:
        return configured
    try:
        return _cached_probe(channel_idx)
    except Exception as exc:  # noqa: BLE001 — the cache backend itself may fail; a probe must not raise
        logger.warning("SMTP probe of channel %s failed: %s", channel_idx, type(exc).__name__)
        return SmtpStatus.UNREACHABLE


def _cached_probe(channel_idx: str) -> SmtpStatus:
    key = CACHE_KEY.format(idx=channel_idx)
    cached = cache.get(key)
    if cached is not None:
        return SmtpStatus(cached)
    result = _probe(channel_entries()[channel_idx])
    if result == SmtpStatus.CONFIGURED:  # a failure is never cached: "Check again" after a fix must log in again
        cache.set(key, result.value, CACHE_TTL_S)
    return result


def _probe(entry: dict) -> SmtpStatus:
    connection = None
    try:
        connection = get_connection(  # raises on EMAIL_USE_SSL and EMAIL_USE_TLS both true
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=entry["EMAIL_HOST"],
            port=entry["EMAIL_PORT"],
            username=entry["EMAIL_HOST_USER"],
            password=entry["EMAIL_HOST_PASSWORD"],
            use_ssl=entry["EMAIL_USE_SSL"],
            use_tls=entry["EMAIL_USE_TLS"],
            timeout=PROBE_TIMEOUT_S,
        )
        connection.open()
    except SMTPAuthenticationError:
        return SmtpStatus.AUTH_FAILED
    except Exception as exc:  # noqa: BLE001 — refused, timeout, TLS: all mean "unreachable" for the UI
        logger.info("SMTP unreachable: %s", type(exc).__name__)
        return SmtpStatus.UNREACHABLE
    finally:
        if connection is not None:
            with contextlib.suppress(Exception):  # QUIT on a dead socket must not turn AUTH_FAILED into UNREACHABLE
                connection.close()
    return SmtpStatus.CONFIGURED
