# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Configuration health checks (tag ``entirius_config``, probes ``entirius_probe``), aggregated by django-munin.

Warnings only: a config gap must never stop ``runserver`` or ``migrate``.
"""

from django.core import checks

from django_email.services.smtp_status import SmtpStatus, channel_entries, missing_keys, smtp_probe

CODE = "email.smtp"
FIX_URL = "https://github.com/entirius/entirius-django-email/blob/master/docs/configuration.md#per-channel-smtp"


class _Subject(dict):
    """Row metadata munin reads as a dict; `manage.py check` prints `str(obj)` as the label, so name the subject."""

    def __str__(self) -> str:
        return self.get("scope") or "settings"


@checks.register("entirius_config", CODE)
def smtp_entries_complete(app_configs=None, **kwargs) -> list[checks.CheckMessage]:
    """An entry with a missing key silently falls back to the global backend (the error is only logged)."""
    return [
        _warning(
            idx,
            SmtpStatus.UNCONFIGURED,
            f"SMTP entry of channel {idx} is incomplete",
            f"EMAIL_SMTP_CONFIGURATION_CHANNELS['{idx}'] lacks or leaves empty {', '.join(missing)}; "
            "mail of this channel goes through the global EMAIL_* backend instead.",
        )
        for idx in channel_entries()
        if (missing := missing_keys(idx))
    ]


@checks.register("entirius_probe", CODE, deploy=True)
def smtp_login(app_configs=None, **kwargs) -> list[checks.CheckMessage]:
    """One SMTP login per complete entry (cached 60 s) — runs only on request, never at boot."""
    results = {idx: smtp_probe(idx) for idx in channel_entries() if not missing_keys(idx)}
    return [
        _warning(idx, state, f"SMTP of channel {idx}: {state.replace('_', ' ')}", _probe_detail(state))
        for idx, state in results.items()
        if state != SmtpStatus.CONFIGURED
    ]


def _probe_detail(state: SmtpStatus) -> str:
    if state == SmtpStatus.AUTH_FAILED:
        return "The server refused EMAIL_HOST_USER / EMAIL_HOST_PASSWORD."
    return "No SMTP session could be opened: check EMAIL_HOST, EMAIL_PORT and EMAIL_USE_SSL / EMAIL_USE_TLS."


def _warning(idx: str, state: SmtpStatus, title: str, detail: str) -> checks.Warning:
    return checks.Warning(
        title,
        hint=detail,
        id=CODE,
        obj=_Subject(scope=idx, state=str(state), severity="high", fix_url=FIX_URL),
    )
