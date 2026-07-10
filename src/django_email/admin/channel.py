# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _
from django_utils.admin.base_admin import BaseModelAdmin as ModelAdmin

from django_email.admin.lang_channel_config import LangChannelConfigInline
from django_email.email_types import EMAIL_TYPE_CHOICES
from django_email.models import Channel


class ChannelAdminForm(forms.ModelForm):
    bcc_email_types = forms.MultipleChoiceField(
        choices=EMAIL_TYPE_CHOICES,
        widget=FilteredSelectMultiple(_("email types"), is_stacked=False),
        required=False,
        help_text=_("Email types for which a BCC copy is sent to the BCC address."),
    )


@admin.register(Channel)
class ChannelAdmin(ModelAdmin):
    form = ChannelAdminForm
    list_display = ("idx", "from_name", "from_email", "from_t9n")
    list_display_links = list_display
    inlines = [LangChannelConfigInline]

    fieldsets = (
        ("Channel", {"fields": ("idx", "label")}),
        (
            "From",
            {
                "description": "Priority: 1. from_t9n, 2. from_name & from_email, 3. settings DEFAULT_FROM_EMAIL",
                "fields": ("from_name", "from_email", "from_t9n"),
            },
        ),
        (
            "BCC",
            {
                "description": (
                    "Send a blind copy (BCC) of the selected email types to an administrator. "
                    "The original recipient does not see that a copy was sent."
                ),
                "fields": ("bcc_email", "bcc_email_types"),
            },
        ),
        (
            "Colors",
            {
                "description": "Setup mail colors in HTML HEX format.",
                "fields": ("main_background_color", "body_background_color", "main_text_color", "brand_text_color"),
            },
        ),
        ("Font", {"description": "Use a CSS compatible font", "fields": ("font_family",)}),
        ("Email esentials", {"fields": ("logo_max_width",)}),
    )
