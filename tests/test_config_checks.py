# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Per-channel SMTP state (`smtp_status` / `smtp_probe`) and the `email.smtp` health checks."""

from smtplib import SMTPAuthenticationError
from unittest.mock import patch

import pytest
from django.core import checks
from django.core.cache import cache

from django_email.checks import smtp_entries_complete, smtp_login
from django_email.services.smtp_status import SmtpStatus, smtp_probe, smtp_status

COMPLETE = {
    "EMAIL_HOST": "smtp.example.com",
    "EMAIL_PORT": 587,
    "EMAIL_HOST_USER": "user",
    "EMAIL_HOST_PASSWORD": "secret",
    "EMAIL_USE_SSL": False,
    "EMAIL_USE_TLS": True,
}
OPEN = "django.core.mail.backends.smtp.EmailBackend.open"


@pytest.fixture(autouse=True)
def _clean_cache():
    cache.clear()


def _channels(entries):
    """`django_email.settings` is frozen at import — `override_settings` never reaches it."""
    return patch("django_email.settings.EMAIL_SMTP_CONFIGURATION_CHANNELS", entries)


class TestSmtpStatus:
    def test_complete_entry_is_configured(self):
        with _channels({"eu": COMPLETE}):
            assert smtp_status("eu") == SmtpStatus.CONFIGURED

    def test_missing_entry_or_setting_is_unconfigured(self):
        with _channels(None):
            assert smtp_status("eu") == SmtpStatus.UNCONFIGURED
        with _channels({"other": COMPLETE}):
            assert smtp_status("eu") == SmtpStatus.UNCONFIGURED

    def test_entry_missing_a_key_is_unconfigured(self):
        partial = {k: v for k, v in COMPLETE.items() if k != "EMAIL_PORT"}
        with _channels({"eu": partial}):
            assert smtp_status("eu") == SmtpStatus.UNCONFIGURED

    @pytest.mark.parametrize("key", ["EMAIL_HOST", "EMAIL_PORT"])
    def test_empty_host_or_port_is_unconfigured(self, key):
        """An unset env var arrives as "" — present but useless."""
        with _channels({"eu": {**COMPLETE, key: ""}}):
            assert smtp_status("eu") == SmtpStatus.UNCONFIGURED

    def test_empty_credentials_and_false_flags_stay_configured(self):
        """Unauthenticated relay: no user, no password, no SSL/TLS is a valid entry."""
        relay = {**COMPLETE, "EMAIL_HOST_USER": "", "EMAIL_HOST_PASSWORD": "", "EMAIL_USE_TLS": False}
        with _channels({"eu": relay}):
            assert smtp_status("eu") == SmtpStatus.CONFIGURED


class TestSmtpProbe:
    def test_login_ok_is_configured_and_cached(self):
        with _channels({"eu": COMPLETE}), patch(OPEN) as open_:
            assert smtp_probe("eu") == SmtpStatus.CONFIGURED
            assert smtp_probe("eu") == SmtpStatus.CONFIGURED
        assert open_.call_count == 1

    def test_a_failure_is_not_cached(self):
        with _channels({"eu": COMPLETE}), patch(OPEN, side_effect=ConnectionRefusedError()) as open_:
            smtp_probe("eu")
            smtp_probe("eu")
        assert open_.call_count == 2

    def test_ssl_and_tls_both_on_is_unreachable_not_a_crash(self):
        with _channels({"eu": {**COMPLETE, "EMAIL_USE_SSL": True}}):
            assert smtp_probe("eu") == SmtpStatus.UNREACHABLE

    def test_rejected_credentials_are_auth_failed(self):
        with _channels({"eu": COMPLETE}), patch(OPEN, side_effect=SMTPAuthenticationError(535, b"no")):
            assert smtp_probe("eu") == SmtpStatus.AUTH_FAILED

    def test_connection_error_is_unreachable(self):
        with _channels({"eu": COMPLETE}), patch(OPEN, side_effect=ConnectionRefusedError()):
            assert smtp_probe("eu") == SmtpStatus.UNREACHABLE

    def test_unconfigured_never_touches_the_network(self):
        with _channels({}), patch(OPEN) as open_:
            assert smtp_probe("eu") == SmtpStatus.UNCONFIGURED
        open_.assert_not_called()


class TestChecks:
    def test_complete_entries_pass(self):
        with _channels({"eu": COMPLETE}):
            assert smtp_entries_complete() == []

    def test_no_per_channel_routing_passes(self):
        with _channels(None):
            assert smtp_entries_complete() == []

    def test_incomplete_entry_is_a_warning_with_scope_and_fix_url(self):
        partial = {k: v for k, v in COMPLETE.items() if k != "EMAIL_HOST_PASSWORD"}
        with _channels({"eu": partial}):
            [message] = smtp_entries_complete()
        assert message.level == checks.WARNING
        assert message.id == "email.smtp"
        assert message.obj["scope"] == "eu"
        assert message.obj["state"] == "unconfigured"
        assert message.obj["fix_url"].startswith("https://")
        assert "EMAIL_HOST_PASSWORD" in message.hint
        assert str(message).startswith("eu: (email.smtp) ")  # CLI label names the channel, not the dict

    def test_probe_reports_auth_failed(self):
        with _channels({"eu": COMPLETE}), patch(OPEN, side_effect=SMTPAuthenticationError(535, b"no")):
            [message] = smtp_login()
        assert message.obj["state"] == "auth_failed"

    def test_checks_are_registered_under_their_tags(self):
        config = checks.registry.registry.get_checks()
        deploy = checks.registry.registry.get_checks(include_deployment_checks=True)
        assert smtp_entries_complete in config
        assert smtp_login not in config
        assert smtp_login in deploy
        assert {"entirius_config", "email.smtp"} <= set(smtp_entries_complete.tags)
        assert {"entirius_probe", "email.smtp"} <= set(smtp_login.tags)


class TestEmailDomainWithoutLogger:
    def test_incomplete_entry_is_no_connection_not_a_crash(self):
        """Communicator and notifications build EmailDomain without set_logger — an incomplete entry must not raise."""
        from django_email.domain import EmailDomain

        partial = {k: v for k, v in COMPLETE.items() if k != "EMAIL_USE_SSL"}
        with _channels({"eu": partial}):
            assert EmailDomain(channel_idx="eu").channel_smtp_connection is None

    def test_failing_quit_keeps_auth_failed(self):
        with (
            _channels({"eu": COMPLETE}),
            patch(OPEN, side_effect=SMTPAuthenticationError(535, b"no")),
            patch("django.core.mail.backends.smtp.EmailBackend.close", side_effect=OSError()),
        ):
            assert smtp_probe("eu") == SmtpStatus.AUTH_FAILED
