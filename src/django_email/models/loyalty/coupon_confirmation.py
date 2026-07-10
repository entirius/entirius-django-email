# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models
from django.utils.translation import gettext as _


class LoyaltyCouponConfirmation(models.Model):
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
    thank_you = models.TextField(null=True, blank=True)
    coupon_copy = models.TextField(null=True, blank=True)
    coupon_button = models.TextField(null=True, blank=True)
    help = models.TextField(null=True, blank=True)

    def subject_as_dict(self) -> dict:
        return {"subject": str(self.subject)} if self.subject else {}

    def variables_as_dict(self, username: str = None) -> dict:
        welcome = _("WelcomeLoyaltyMessage")
        return {
            "welcome": (
                str(self.welcome).replace("|user_name|", username) if self.welcome else f"{welcome} {username}"
            ),
            "thank_you": self.thank_you or _("ThankYouLoyaltyMessage"),
            "coupon_copy": self.coupon_copy or _("ConfirmCouponMessage"),
            "coupon_button": self.coupon_button or _("CouponButtonMessage"),
            "help": self.help or _("CouponIgnoreMessage"),
        }

    def __str__(self) -> str:
        return f"{self.channel.idx} - {self.language.iso2}"

    class Meta:
        app_label = "django_email"
        verbose_name = "[Loyalty] Coupon Confirmation"
        verbose_name_plural = "[Loyalty] Coupon Confirmations"
