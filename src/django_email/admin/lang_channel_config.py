# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.contrib import admin
from django_utils.admin.base_admin import BaseModelAdmin as ModelAdmin

from django_email.models import LangChannelConfig


class LangChannelConfigInline(admin.TabularInline):
    model = LangChannelConfig
    extra = 0
    fields = (
        "language",
        "shop_name",
        "logo_url",
        "header_mail",
        "footer_copy",
        "footer_name_brand",
        "footer_link_brand",
        "footer_link_facebook",
        "footer_link_instagram",
        "footer_link_youtube",
        "footer_link_x",
        "footer_link_tiktok",
    )


@admin.register(LangChannelConfig)
class LangChannelConfigAdmin(ModelAdmin):
    list_display = ("channel", "language", "shop_name", "header_mail")
    list_display_links = list_display
    list_filter = ("channel", "language")
    search_fields = ("channel__idx", "language", "shop_name")

    fieldsets = (
        ("Configuration", {"fields": ("channel", "language")}),
        ("Email essentials", {"fields": ("shop_name", "logo_url")}),
        ("Header", {"fields": ("header_mail",)}),
        ("Footer", {"fields": ("footer_copy", "footer_name_brand", "footer_link_brand")}),
        (
            "Footer - Social Media",
            {
                "description": "Links to Social Media accounts.",
                "fields": (
                    "footer_link_facebook",
                    "footer_link_instagram",
                    "footer_link_youtube",
                    "footer_link_x",
                    "footer_link_tiktok",
                ),
            },
        ),
    )
