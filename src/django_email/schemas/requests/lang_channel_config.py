# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pydantic import BaseModel, Field

from django_email.schemas.validators import WysiwygStr


class LangChannelConfigUpdateRequest(BaseModel):
    shop_name: str | None = Field(None, description="Store display name", examples=["My Store"])
    logo_url: str | None = Field(None, description="Logo image URL")
    header_mail: str | None = Field(None, description="Support email in header", examples=["support@store.com"])
    footer_copy: WysiwygStr = Field(None, description="Footer text copy (WYSIWYG; empty = no copy)")
    footer_name_brand: str | None = Field(None, description="Brand name in footer")
    footer_link_brand: str | None = Field(None, description="Brand URL in footer")
    footer_link_facebook: str | None = Field(None, description="Facebook URL")
    footer_link_instagram: str | None = Field(None, description="Instagram URL")
    footer_link_youtube: str | None = Field(None, description="YouTube URL")
    footer_link_x: str | None = Field(None, description="X (Twitter) URL")
    footer_link_tiktok: str | None = Field(None, description="TikTok URL")
    footer_signature_copy_1: str | None = Field(
        None, description="First line of footer signature. Empty = use translated default.", max_length=512
    )
    footer_signature_copy_2: str | None = Field(
        None, description="Second line of footer signature, rendered next to brand link", max_length=512
    )
    footer_socials_copy: str | None = Field(None, description="Copy displayed before social links", max_length=512)
    footer_automatic_copy: WysiwygStr = Field(
        None,
        description="Plain-text disclaimer. Newlines render as <br>; HTML is auto-escaped.",
        max_length=2048,
    )
    footer_unsubscribe_label: str | None = Field(None, description="Label for the unsubscribe link", max_length=256)
