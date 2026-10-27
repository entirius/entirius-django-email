# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for the EMAIL_ADMIN_API_ENABLED toggle.

When the setting is False the admin API (v2) must not be mounted in the urlconf
and its DRF/pydantic/drf-spectacular imports must never be triggered. Enabled by
default.
"""

import importlib

import pytest
from django.test import override_settings
from django.urls import clear_url_caches
from rest_framework.test import APIClient

import django_email.settings as email_settings
import django_email.urls as email_urls

ADMIN_API_PREFIX = "api/email/v2/admin/"
CHANNELS_URL = f"/{ADMIN_API_PREFIX}default-europe/channels/"


def _rebuild_urlpatterns() -> list:
    """Reload module settings + urlconf so they re-read EMAIL_ADMIN_API_ENABLED."""
    importlib.reload(email_settings)
    importlib.reload(email_urls)
    clear_url_caches()
    return email_urls.urlpatterns


@pytest.fixture(autouse=True)
def _restore_default_urlconf():
    # Leave the urlconf in its default (enabled) state for every other test module.
    yield
    importlib.reload(email_settings)
    importlib.reload(email_urls)
    clear_url_caches()


def test_admin_api_is_mounted_by_default():
    patterns = _rebuild_urlpatterns()

    assert len(patterns) == 1
    assert str(patterns[0].pattern) == ADMIN_API_PREFIX


@override_settings(EMAIL_ADMIN_API_ENABLED=False)
def test_admin_api_absent_from_urlconf_when_disabled():
    patterns = _rebuild_urlpatterns()

    assert patterns == []


@override_settings(EMAIL_ADMIN_API_ENABLED=False)
def test_admin_api_endpoint_returns_404_when_disabled():
    _rebuild_urlpatterns()

    response = APIClient().get(CHANNELS_URL)

    assert response.status_code == 404
