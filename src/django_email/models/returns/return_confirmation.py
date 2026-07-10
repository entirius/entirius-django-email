# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models
from django.utils.translation import gettext as _


class ReturnsReturnConfirmation(models.Model):
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
    return_copy = models.TextField(
        null=True,
        blank=True,
        help_text="If you want to add order ID or return ID, please fill this field with |order_id| |return_id|",
    )
    comment_copy = models.TextField(null=True, blank=True)
    print_copy = models.TextField(null=True, blank=True)
    help = models.TextField(null=True, blank=True)

    def subject_as_dict(self) -> dict:
        return {"subject": str(self.subject)} if self.subject else {}

    def variables_as_dict(self, username: str = None, order_id: str = None, return_id: str = None) -> dict:
        welcome = _("WelcomeReturnMessage")
        return_m1 = _("ReturnMessage1")
        return_m2 = _("ReturnMessage2")
        return {
            "welcome": (
                str(self.welcome).replace("|user_name|", username) if self.welcome else f"{welcome} {username}"
            ),
            "return_copy": (
                str(self.return_copy).replace("|order_id|", order_id).replace("|return_id|", return_id)
                if self.return_copy
                else f"{return_m1}, {order_id} {return_m2} {return_id}"
            ),
            "comment_copy": self.comment_copy or _("Comment"),
            "print_copy": self.print_copy or _("PrintMessage"),
            "help": self.help or _("ReturnMessage3"),
        }

    def __str__(self) -> str:
        return f"{self.channel.idx} - {self.language.iso2}"

    class Meta:
        app_label = "django_email"
        verbose_name = "[Returns] Return Confirmation"
        verbose_name_plural = "[Returns] Return Confirmations"
