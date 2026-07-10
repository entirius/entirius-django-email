# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models

from django_email.models.contact_forms.submission_facts import SubmissionFactsEmail


class ContactFormsClientCopy(SubmissionFactsEmail):
    """Operator-editable copy sent to the submitter (the customer), not the
    admin. Shares the submission-facts shape with ContactFormsSubmission so the
    client confirmation can carry its own subject/copy ("thank you, we received
    your message") while reusing the same facts table."""

    header_title = models.TextField(
        blank=True,
        default="",
        help_text="H2 heading at the top of the email. Overrides 'Thank you for contacting us' default.",
    )

    class Meta:
        app_label = "django_email"
        verbose_name = "[Contact Forms] Client Copy"
        verbose_name_plural = "[Contact Forms] Client Copies"
