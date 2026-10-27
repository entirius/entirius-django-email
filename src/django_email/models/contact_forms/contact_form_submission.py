# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models

from django_email.models.contact_forms.submission_facts import SubmissionFactsEmail


class ContactFormsSubmission(SubmissionFactsEmail):
    subject = models.CharField(
        max_length=256,
        blank=True,
        default="",
        help_text=(
            "Email subject. Put <contact_form_id> in the text to have the submission id "
            "substituted there — that is what gives every notification its own mail "
            "thread instead of stacking them in one. Leave the token out and no id is added."
        ),
    )
    header_title = models.TextField(
        blank=True,
        default="",
        help_text="H2 heading at the top of the email. Overrides 'New contact form submission' default.",
    )

    class Meta:
        app_label = "django_email"
        verbose_name = "[Contact Forms] Submission"
        verbose_name_plural = "[Contact Forms] Submissions"
