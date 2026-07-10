# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models
from django.utils.translation import gettext as _


class AgreementsNewsletterSignup(models.Model):
    channel = models.ForeignKey("Channel", on_delete=models.CASCADE)
    language = models.ForeignKey(
        "django_regional.Language",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only languages that are enabled in django_email setting EMAIL_AVAILABLE_LANGUAGES works.",
    )
    subject = models.CharField(max_length=256, null=True, blank=True)
    welcome = models.TextField(
        null=True, blank=True, help_text="If you want to add user name, please fill this field with |user_name|"
    )
    confirm_copy = models.TextField(null=True, blank=True)
    confirm_button = models.TextField(null=True, blank=True)
    help = models.TextField(null=True, blank=True)

    def subject_as_dict(self) -> dict:
        return {"subject": str(self.subject)} if self.subject else {}

    def variables_as_dict(self, username: str = None) -> dict:
        welcome = _("NewsletterWelcomeMessage")
        return {
            "welcome": (
                str(self.welcome).replace("|user_name|", username)
                if self.welcome and username
                else self.welcome or f"{welcome}"
            ),
            "confirm_copy": self.confirm_copy or _("NewsletterConfirmMessage"),
            "confirm_button": self.confirm_button or _("NewsletterConfirmButton"),
            "help": self.help or _("NewsletterHelpMessage"),
        }

    def __str__(self) -> str:
        lang = self.language.iso2 if self.language else "default"
        return f"{self.channel.idx} - {lang}"

    class Meta:
        app_label = "django_email"
        verbose_name = "[Agreements] Newsletter Signup"
        verbose_name_plural = "[Agreements] Newsletter Signups"
