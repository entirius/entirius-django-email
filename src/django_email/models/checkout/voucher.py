# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Shared template config for voucher emails.

Used by 3 EmailService subclasses (issued_on_purchase, issued_by_admin, resend).
Single model = single migration, fewer rows for admins to manage per channel.
"""

from django.db import models
from django.utils.translation import gettext as _


class CheckoutVoucher(models.Model):
    KIND_ISSUED_ON_PURCHASE = "issued_on_purchase"
    KIND_ISSUED_BY_ADMIN = "issued_by_admin"
    KIND_RESEND = "resend"

    channel = models.ForeignKey("Channel", on_delete=models.CASCADE)
    language = models.ForeignKey(
        "django_regional.Language",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only languages enabled in EMAIL_AVAILABLE_LANGUAGES are honored.",
    )

    # Per-kind subjects (placeholder |voucher_code| replaced at send time)
    issued_on_purchase_subject = models.CharField(max_length=256, null=True, blank=True)
    issued_by_admin_subject = models.CharField(max_length=256, null=True, blank=True)
    resend_subject = models.CharField(max_length=256, null=True, blank=True)

    # Shared body copy
    welcome = models.TextField(null=True, blank=True)
    code_label = models.CharField(max_length=128, null=True, blank=True)
    pin_label = models.CharField(max_length=128, null=True, blank=True)
    expires_label = models.CharField(max_length=128, null=True, blank=True)
    balance_label = models.CharField(max_length=128, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    help = models.TextField(null=True, blank=True)

    def subject_for(self, kind: str) -> dict:
        mapping = {
            self.KIND_ISSUED_ON_PURCHASE: self.issued_on_purchase_subject,
            self.KIND_ISSUED_BY_ADMIN: self.issued_by_admin_subject,
            self.KIND_RESEND: self.resend_subject,
        }
        subject = mapping.get(kind)
        return {"subject": str(subject)} if subject else {}

    def variables_as_dict(self) -> dict:
        return {
            "welcome": self.welcome or _("Hello! Your voucher is ready to use."),
            "code_label": self.code_label or _("Your voucher code:"),
            "pin_label": self.pin_label or _("PIN:"),
            "expires_label": self.expires_label or _("Valid until:"),
            "balance_label": self.balance_label or _("Value:"),
            "instructions_copy": self.instructions
            or _(
                "Use the code above at checkout. The voucher can be used multiple times until the balance reaches zero."
            ),
            "help": self.help or _("If you did not request this voucher, please ignore this message."),
        }

    def __str__(self) -> str:
        lang = self.language.iso2 if self.language else "—"
        return f"{self.channel.idx} - {lang}"

    class Meta:
        app_label = "django_email"
        verbose_name = "[Checkout] Voucher Email"
        verbose_name_plural = "[Checkout] Voucher Emails"
