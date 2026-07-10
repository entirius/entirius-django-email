# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models
from django.utils.translation import gettext as _


class AllegroVirtualProduct(models.Model):
    channel = models.ForeignKey("Channel", on_delete=models.CASCADE)
    language = models.ForeignKey(
        "django_regional.Language",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only languages that are enabled in django_email setting EMAIL_AVAILABLE_LANGUAGES works.",
    )
    subject = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="If you want order number in subject, please fill this field with |order_id|",
    )
    welcome = models.TextField(
        null=True, blank=True, help_text="If you want to add user name, please fill this field with |user_name|"
    )
    order = models.TextField(
        null=True, blank=True, help_text="If you want to add order number, please fill this field with |order_id|"
    )
    products = models.TextField(null=True, blank=True)
    key_name = models.CharField(max_length=256, null=True, blank=True)
    additional_key_name = models.CharField(max_length=256, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    help = models.TextField(null=True, blank=True)

    def subject_as_dict(self, order_id: str = None) -> dict:
        return {"subject": str(self.subject).replace("|order_id|", order_id)} if self.subject else {}

    def variables_as_dict(self, username: str = None, order_id: str = None) -> dict:
        welcome = _("WelcomeOrderMessage")
        order = _("ThankYouOrderMessage")
        return {
            "welcome": (
                str(self.welcome).replace("|user_name|", username) if self.welcome else f"{welcome} {username}"
            ),
            "order": (str(self.order).replace("|order_id|", order_id) if self.order else f"{order} {order_id}"),
            "products_copy": self.products or _("Products"),
            "key_name": str(self.key_name),
            "additional_key_name": str(self.additional_key_name),
            "instructions_copy": self.instructions or _("Instructions"),
            "help": self.help or _("IgnoreOrderMessage"),
        }

    def __str__(self) -> str:
        return f"{self.channel.idx} - {self.language.iso2}"

    class Meta:
        app_label = "django_email"
        verbose_name = "[Allegro] Virtual Product"
        verbose_name_plural = "[Allegro] Virtual Products"
