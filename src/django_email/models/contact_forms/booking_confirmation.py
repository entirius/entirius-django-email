# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models


class ContactFormsBookingConfirmation(models.Model):
    channel = models.ForeignKey("Channel", on_delete=models.CASCADE)
    language = models.ForeignKey(
        "django_regional.Language",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only languages that are enabled in django_email setting EMAIL_AVAILABLE_LANGUAGES works.",
    )
    subject = models.CharField(max_length=256, blank=True, default="")
    header_title = models.TextField(
        blank=True,
        default="",
        help_text="H2 heading at the top of the email. Overrides 'Your booking is confirmed' default.",
    )
    greeting_template = models.TextField(
        blank=True,
        default="",
        help_text="Greeting line. Use placeholder |booker_name| where the booker's name should appear "
        "(e.g., 'Cześć |booker_name|,'). Leave empty for translated default.",
    )
    intro_copy = models.TextField(blank=True, default="", help_text="Paragraph rendered above the booking facts.")
    label_datetime = models.CharField(
        max_length=256, blank=True, default="", help_text="Table label for the date & time row."
    )
    label_email = models.CharField(max_length=256, blank=True, default="", help_text="Table label for the email row.")
    label_phone = models.CharField(max_length=256, blank=True, default="", help_text="Table label for the phone row.")
    label_company = models.CharField(
        max_length=256, blank=True, default="", help_text="Table label for the company row."
    )
    label_message = models.CharField(
        max_length=256, blank=True, default="", help_text="Table label for the message row."
    )
    label_video = models.CharField(
        max_length=256, blank=True, default="", help_text="Inline label before the video meeting link."
    )
    closing_copy = models.TextField(blank=True, default="", help_text="Paragraph rendered after the meet link.")

    class Meta:
        app_label = "django_email"
        verbose_name = "[Contact Forms] Booking Confirmation"
        verbose_name_plural = "[Contact Forms] Booking Confirmations"

    def __str__(self) -> str:
        lang = self.language.iso2 if self.language else "default"
        return f"{self.channel.idx} - {lang}"

    def subject_as_dict(self) -> dict:
        return {"subject": str(self.subject)} if self.subject else {}

    def variables_as_dict(self) -> dict:
        # Empty-string fallback (vs. gettext-keyed like AgreementsNewsletterSignup):
        # our booking templates ship natural-English {% else %} branches per
        # docs/multilang-emails.md, so truthy defaults here would bypass them.
        # `greeting_template` is left raw — the service resolves |booker_name|
        # placeholder in prepare_context() because the booker name isn't on the model.
        return {
            "header_title": self.header_title or "",
            "greeting_template": self.greeting_template or "",
            "intro_copy": self.intro_copy or "",
            "label_datetime": self.label_datetime or "",
            "label_email": self.label_email or "",
            "label_phone": self.label_phone or "",
            "label_company": self.label_company or "",
            "label_message": self.label_message or "",
            "label_video": self.label_video or "",
            "closing_copy": self.closing_copy or "",
        }
