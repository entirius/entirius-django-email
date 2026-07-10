# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Canonical language-resolution helper for email callers.

One place for the rule documented in docs/multilang-emails.md and
rules/python/language-handling.md: prefer the explicit user choice, fall
back to the channel default, let EmailService._activate_language handle
the final EMAIL_DEFAULT_LANGUAGE fallback silently.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_email.models import Channel


def resolve_email_language(requested_iso2: str | None, channel: Channel | None) -> str | None:
    """Return an ISO 639-1 code for the email render, or ``None``.

    - ``requested_iso2`` wins when truthy (schema-validated value from the caller).
    - Otherwise falls back to ``channel.default_language.iso2``.
    - ``None`` return defers to ``EMAIL_DEFAULT_LANGUAGE`` inside
      ``EmailService._activate_language`` (silent fallback per
      api-response-contract.md — never raise 400 for an unknown code).
    """
    if requested_iso2:
        return requested_iso2
    if channel and channel.default_language:
        return channel.default_language.iso2
    return None
