# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for EmailService.send_prerendered.

A caller-rendered body is wrapped in the shared layout (base/header + base/footer
+ channel branding) instead of a flow template, and goes out with both a
text/plain and a text/html part.
"""

import pytest
from django.core import mail

from django_email.service.checkout.voucher_issued_on_purchase import VoucherIssuedOnPurchaseEmailService

from .factories import ChannelFactory, LangChannelConfigFactory, _get_or_create_language

LOCMEM = "django.core.mail.backends.locmem.EmailBackend"
RECIPIENT = "user@example.com"


@pytest.fixture
def service(db, settings):
    """EmailService bound to a channel with branding, sending to the in-memory backend."""
    settings.EMAIL_BACKEND = LOCMEM
    mail.outbox = []
    channel = ChannelFactory()
    LangChannelConfigFactory(channel=channel, shop_name="My Shop", footer_name_brand="My Brand")
    _get_or_create_language("en")
    return VoucherIssuedOnPurchaseEmailService(language="en", channel_idx=channel.idx)


def test_html_part_keeps_the_body_unescaped(service):
    service.send_prerendered([RECIPIENT], subject="Subject", html_message="<p>Hello</p>", message="Hello")

    html, content_type = mail.outbox[0].alternatives[0]
    assert content_type == "text/html"
    assert "<p>Hello</p>" in html


def test_body_is_wrapped_in_header_and_footer(service):
    service.send_prerendered([RECIPIENT], subject="Subject", html_message="<p>Hello</p>", message="Hello")

    html = mail.outbox[0].alternatives[0][0]
    assert "My Shop" in html
    assert "My Brand" in html
    assert "None" not in html


def test_caller_subject_wins_over_template_variables(service):
    service.send_prerendered([RECIPIENT], subject="Caller subject", html_message="<p>Hello</p>", message="Hello")

    message = mail.outbox[0]
    assert message.subject == "Caller subject"
    assert "<title>Caller subject</title>" in message.alternatives[0][0]


def test_plain_text_alternative_and_recipient(service):
    service.send_prerendered([RECIPIENT], subject="Subject", html_message="<p>Hello</p>", message="Hello")

    message = mail.outbox[0]
    assert message.to == [RECIPIENT]
    assert message.body == "Hello"
