# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models


class Channel(models.Model):
    idx = models.CharField(max_length=64)
    label = models.CharField(max_length=64)
    from_name = models.CharField(max_length=256, null=True, blank=True)
    from_email = models.EmailField(null=True, blank=True)
    from_t9n = models.JSONField(
        null=True, blank=True, help_text="Should be in format: {pl: {from_name: ABC, from_email: abc@example.com}}"
    )
    main_background_color = models.CharField(max_length=10, default="#FFFFFF")
    body_background_color = models.CharField(max_length=10, default="#EDEDED")
    main_text_color = models.CharField(max_length=10, default="#141414")
    brand_text_color = models.CharField(max_length=10, default="#404040")
    font_family = models.CharField(max_length=256, default="'Inter', sans-serif")
    logo_max_width = models.CharField(max_length=20, default="100")
    bcc_email = models.EmailField(
        null=True,
        blank=True,
        help_text=(
            "Administrator address that receives a blind carbon copy (BCC) of selected emails. "
            "The original recipient does not see that a copy was sent."
        ),
    )
    bcc_email_types = models.JSONField(
        default=list,
        blank=True,
        help_text="Email types for which a BCC copy is sent to the BCC address.",
    )

    def get_bcc_recipients(self, email_name: str) -> list[str]:
        """Return the BCC recipient list for the given email type.

        A BCC is sent only when a ``bcc_email`` is configured and the email type
        (the service ``EMAIL_NAME``) is selected in ``bcc_email_types``.
        """
        if self.bcc_email and email_name and email_name in (self.bcc_email_types or []):
            return [self.bcc_email]
        return []

    def get_lang_config(self, lang: str):
        """
        Get language-specific configuration for this channel.
        Priority: specific language config > default config (language=None)
        """
        from django_email.models.lang_channel_config import LangChannelConfig

        lang_config = LangChannelConfig.objects.filter(channel=self, language=lang).first()

        if not lang_config:
            lang_config = LangChannelConfig.objects.filter(channel=self, language__isnull=True).first()

        return lang_config

    def variables_as_dict(self, lang) -> dict:
        """
        Return all template variables including channel-level and language-specific config.
        """
        variables = {
            "main_bgc": self.main_background_color,
            "body_bgc": self.body_background_color,
            "main_text_clr": self.main_text_color,
            "brand_text_clr": self.brand_text_color,
            "font_family": self.font_family,
            "logo_max_width": self.logo_max_width,
        }

        # Add language-specific config if available
        lang_config = self.get_lang_config(lang)
        if lang_config:
            variables.update(lang_config.variables_as_dict())

        return variables

    class Meta:
        app_label = "django_email"

    def __str__(self) -> str:
        return f"{self.idx}"
