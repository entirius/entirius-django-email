# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models
from django.utils.translation import gettext as _


class AccountsNewAccount(models.Model):
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
    announce = models.TextField(null=True, blank=True)
    confirm_button = models.TextField(null=True, blank=True)
    thank_you = models.TextField(null=True, blank=True)
    help = models.TextField(null=True, blank=True)

    def subject_as_dict(self) -> dict:
        return {"subject": str(self.subject)} if self.subject else {}

    def variables_as_dict(self, username: str = None) -> dict:
        welcome = _("WelcomeAccountMessage")
        return {
            "welcome": (
                str(self.welcome).replace("|user_name|", username) if self.welcome else f"{welcome} {username}"
            ),
            "announce": self.announce or _("AnnounceMessage"),
            "confirm_button": self.confirm_button or _("ConfirmRequestMessage"),
            "thank_you": self.thank_you or _("ThankYouMessage"),
            "help": self.help or _("IgnoreAccountMessage"),
        }

    def __str__(self) -> str:
        return f"{self.channel.idx} - {self.language.iso2}"

    class Meta:
        app_label = "django_email"
        verbose_name = "[Accounts] New Account"
        verbose_name_plural = "[Accounts] New Accounts"
