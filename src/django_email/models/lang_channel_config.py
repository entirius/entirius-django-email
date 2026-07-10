# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models

from django_email.models.channel import Channel


class LangChannelConfig(models.Model):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="lang_configs",
        help_text="Channel to which this configuration belongs.",
    )
    language = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="ISO2 language code (e.g., 'pl', 'en'). Leave empty for default/fallback configuration. "
        "Priority: specific language (e.g., 'pl') takes precedence over default (None).",
    )
    shop_name = models.CharField(max_length=256, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    header_mail = models.EmailField()
    footer_copy = models.TextField(null=True, blank=True, help_text="Footer copy text for this language")
    footer_name_brand = models.CharField(max_length=256, null=True, blank=True)
    footer_link_brand = models.URLField(null=True, blank=True)
    footer_link_facebook = models.URLField(null=True, blank=True)
    footer_link_instagram = models.URLField(null=True, blank=True)
    footer_link_youtube = models.URLField(null=True, blank=True)
    footer_link_x = models.URLField(null=True, blank=True)
    footer_link_tiktok = models.URLField(null=True, blank=True)
    footer_signature_copy_1 = models.TextField(
        blank=True,
        default="",
        help_text="First line of footer signature (e.g., 'Pozdrawiamy,'). Leave empty to use translated default.",
    )
    footer_signature_copy_2 = models.TextField(
        blank=True,
        default="",
        help_text="Second line of footer signature (e.g., 'Ekipa'). Rendered next to brand link.",
    )
    footer_socials_copy = models.TextField(
        blank=True, default="", help_text="Copy displayed before social links (e.g., 'Obserwuj nas:')."
    )
    footer_automatic_copy = models.TextField(
        blank=True,
        default="",
        help_text="Disclaimer at the bottom of every email (e.g., 'To jest wiadomość automatyczna...').",
    )
    footer_unsubscribe_label = models.TextField(
        blank=True, default="", help_text="Label for the unsubscribe link (e.g., 'Wypisz się')."
    )

    class Meta:
        app_label = "django_email"
        unique_together = [["channel", "language"]]
        ordering = ["channel", "language"]

    def __str__(self) -> str:
        lang_label = self.language or "default"
        return f"{self.channel.idx} - {lang_label}"

    def variables_as_dict(self) -> dict:
        """Return variables for template context"""
        return {
            "shop_name": self.shop_name,
            "logo_url": self.logo_url,
            "header_mail": self.header_mail,
            "footer_copy": self.footer_copy,
            "footer_name_brand": self.footer_name_brand,
            "footer_link_brand": self.footer_link_brand,
            "footer_link_fb": self.footer_link_facebook,
            "footer_link_ig": self.footer_link_instagram,
            "footer_link_yt": self.footer_link_youtube,
            "footer_link_x": self.footer_link_x,
            "footer_link_tiktok": self.footer_link_tiktok,
            "footer_signature_copy_1": self.footer_signature_copy_1,
            "footer_signature_copy_2": self.footer_signature_copy_2,
            "footer_socials_copy": self.footer_socials_copy,
            "footer_automatic_copy": self.footer_automatic_copy,
            "footer_unsubscribe_label": self.footer_unsubscribe_label,
        }
