# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for the per-channel administrator BCC feature.

A channel can be configured with a ``bcc_email`` and a list of ``bcc_email_types``
(service ``EMAIL_NAME`` identifiers). When an email of a selected type is sent,
a blind carbon copy goes to the administrator address. BCC (not CC) is used so
the original recipient never sees that a copy was sent.
"""

import pytest
from django.core import mail
from process_logger import ProcessLogger

from django_email.domain import EmailDomain
from django_email.models import Channel

LOCMEM = "django.core.mail.backends.locmem.EmailBackend"


def _domain(bcc: list[str] | None = None) -> EmailDomain:
    """Build an EmailDomain wired up the way EmailService does (logger + from)."""
    domain = EmailDomain()
    domain.set_logger(ProcessLogger("TEST_BCC"))
    domain.set_from_email("from@shop.com")
    if bcc is not None:
        domain.set_bcc(bcc)
    return domain


@pytest.fixture
def locmem_email(settings):
    """Route mail through the in-memory backend and start with an empty outbox."""
    settings.EMAIL_BACKEND = LOCMEM
    mail.outbox = []


class TestChannelGetBccRecipients:
    """Channel.get_bcc_recipients gates BCC on configured address + selected type."""

    def test_returns_bcc_when_type_selected(self):
        channel = Channel(
            bcc_email="admin@shop.com",
            bcc_email_types=["SIGNUP_CONFIRMATION", "ORDER_VIRTUAL_COMPLETE"],
        )
        assert channel.get_bcc_recipients("SIGNUP_CONFIRMATION") == ["admin@shop.com"]

    def test_empty_when_type_not_selected(self):
        channel = Channel(bcc_email="admin@shop.com", bcc_email_types=["ORDER_VIRTUAL_COMPLETE"])
        assert channel.get_bcc_recipients("SIGNUP_CONFIRMATION") == []

    def test_empty_when_no_bcc_email(self):
        channel = Channel(bcc_email=None, bcc_email_types=["SIGNUP_CONFIRMATION"])
        assert channel.get_bcc_recipients("SIGNUP_CONFIRMATION") == []

    def test_empty_when_no_types_configured(self):
        channel = Channel(bcc_email="admin@shop.com", bcc_email_types=[])
        assert channel.get_bcc_recipients("SIGNUP_CONFIRMATION") == []

    def test_empty_when_email_name_is_none(self):
        channel = Channel(bcc_email="admin@shop.com", bcc_email_types=["SIGNUP_CONFIRMATION"])
        assert channel.get_bcc_recipients(None) == []


@pytest.mark.usefixtures("locmem_email")
class TestDomainBcc:
    """EmailDomain attaches the configured BCC to every send path."""

    def test_send_email_without_bcc(self):
        domain = _domain()
        domain.send_email(subject="Hi", message="body", recipient_list=["user@x.com"], html_message="<b>body</b>")

        assert len(mail.outbox) == 1
        assert mail.outbox[0].bcc == []

    def test_send_email_with_bcc(self):
        domain = _domain(["admin@shop.com"])
        domain.send_email(subject="Hi", message="body", recipient_list=["user@x.com"], html_message="<b>body</b>")

        msg = mail.outbox[0]
        # Recipient does not see the copy: admin is in BCC, not To/CC.
        assert msg.bcc == ["admin@shop.com"]
        assert msg.to == ["user@x.com"]
        assert msg.cc == []
        # Reaches the SMTP envelope so the copy is actually delivered.
        assert "admin@shop.com" in msg.recipients()
        # text + html are both preserved.
        assert msg.body == "body"
        assert msg.alternatives == [("<b>body</b>", "text/html")]

    def test_send_email_with_bcc_and_extra_headers(self):
        domain = _domain(["admin@shop.com"])
        domain.send_email(
            subject="Hi",
            message="body",
            recipient_list=["user@x.com"],
            html_message="<b>body</b>",
            extra_headers={"List-Unsubscribe": "<https://x.com/unsub>"},
        )

        msg = mail.outbox[0]
        assert msg.bcc == ["admin@shop.com"]
        assert msg.extra_headers.get("List-Unsubscribe") == "<https://x.com/unsub>"

    def test_set_bcc_empty_clears_to_none(self):
        domain = _domain([])
        domain.send_email(subject="Hi", message="body", recipient_list=["user@x.com"])

        assert mail.outbox[0].bcc == []

    def test_attachments_path_includes_bcc(self, tmp_path):
        attachment = tmp_path / "file.txt"
        attachment.write_text("hello")

        domain = _domain(["admin@shop.com"])
        domain.send_email_with_attachments(
            subject="Hi",
            recipient_list=["user@x.com"],
            html_message="<b>body</b>",
            attachments=[EmailDomain.Attachment.from_path(str(attachment))],
        )

        assert mail.outbox[0].bcc == ["admin@shop.com"]
