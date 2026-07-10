# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models


class CheckoutInvoice(models.Model):
    channel = models.ForeignKey("Channel", on_delete=models.CASCADE)
    language = models.ForeignKey(
        "django_regional.Language",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only languages enabled in EMAIL_AVAILABLE_LANGUAGES setting work.",
    )
    subject = models.CharField(
        max_length=256, null=True, blank=True, help_text="Email subject. Use |order_id| as placeholder."
    )
    intro = models.TextField(
        null=True, blank=True, help_text="Intro text. Use |user_name| and |order_id| as placeholders."
    )
    body = models.TextField(null=True, blank=True, help_text="Main body text.")
    footer = models.TextField(null=True, blank=True)

    def subject_as_dict(self, order_id: str = None) -> dict:
        if self.subject:
            return {"subject": str(self.subject).replace("|order_id|", order_id or "")}
        return {}

    def variables_as_dict(self, username: str = None, order_id: str = None) -> dict:
        return {
            "intro": (
                str(self.intro).replace("|user_name|", username or "").replace("|order_id|", order_id or "")
                if self.intro
                else ""
            ),
            "body": self.body or "",
            "footer": self.footer or "",
        }

    def __str__(self) -> str:
        return f"{self.channel.idx} - {self.language.iso2 if self.language else 'no lang'}"

    class Meta:
        app_label = "django_email"
        verbose_name = "[Checkout] Invoice"
        verbose_name_plural = "[Checkout] Invoices"
