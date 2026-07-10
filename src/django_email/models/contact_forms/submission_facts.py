# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models


class SubmissionFactsEmail(models.Model):
    """Abstract base for submission-shaped contact-form emails.

    Shared by the admin notification (``ContactFormsSubmission``) and the
    submitter copy (``ContactFormsClientCopy``): same channel/language plus an
    editable subject, intro/closing copy, and per-row table labels. Concrete
    subclasses add ``header_title`` (each documents its own default heading) and
    their ``Meta`` (app_label, verbose_name).
    """

    channel = models.ForeignKey("Channel", on_delete=models.CASCADE)
    language = models.ForeignKey(
        "django_regional.Language",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only languages that are enabled in django_email setting EMAIL_AVAILABLE_LANGUAGES works.",
    )
    subject = models.CharField(max_length=256, blank=True, default="")
    intro_copy = models.TextField(blank=True, default="", help_text="Paragraph rendered above the submission facts.")
    label_email = models.CharField(max_length=256, blank=True, default="", help_text="Table label for the email row.")
    label_type = models.CharField(max_length=256, blank=True, default="", help_text="Table label for the type row.")
    label_form = models.CharField(max_length=256, blank=True, default="", help_text="Table label for the form row.")
    label_code = models.CharField(max_length=256, blank=True, default="", help_text="Table label for the code row.")
    label_body = models.CharField(max_length=256, blank=True, default="", help_text="Table label for the body row.")
    closing_copy = models.TextField(blank=True, default="", help_text="Paragraph rendered after the body.")

    class Meta:
        abstract = True

    def __str__(self) -> str:
        lang = self.language.iso2 if self.language else "default"
        return f"{self.channel.idx} - {lang}"

    def subject_as_dict(self) -> dict:
        return {"subject": str(self.subject)} if self.subject else {}

    def variables_as_dict(self) -> dict:
        return {
            "header_title": self.header_title or "",
            "intro_copy": self.intro_copy or "",
            "label_email": self.label_email or "",
            "label_type": self.label_type or "",
            "label_form": self.label_form or "",
            "label_code": self.label_code or "",
            "label_body": self.label_body or "",
            "closing_copy": self.closing_copy or "",
        }
