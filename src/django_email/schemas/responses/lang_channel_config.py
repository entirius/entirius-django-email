# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

# Footer override fields use `default=""` on the model but the API contract requires
# absent values to be null. Coerce empty strings to None on response.
NullableStr = Annotated[str | None, BeforeValidator(lambda v: None if v == "" else v)]


class LangChannelConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    channel_id: int = Field(description="Channel FK", examples=[1])
    language: str | None = Field(None, description="ISO2 language code, null for default", examples=["en"])
    shop_name: str | None = Field(None, description="Store display name", examples=["My Store"])
    logo_url: str | None = Field(None, description="Logo image URL", examples=["https://store.com/logo.png"])
    header_mail: str = Field(description="Support email in header", examples=["support@store.com"])
    footer_copy: str | None = Field(None, description="Footer text copy", examples=["All rights reserved."])
    footer_name_brand: str | None = Field(None, description="Brand name in footer", examples=["My Store"])
    footer_link_brand: str | None = Field(None, description="Brand URL in footer", examples=["https://store.com"])
    footer_link_facebook: str | None = Field(None, description="Facebook URL", examples=["https://facebook.com/store"])
    footer_link_instagram: str | None = Field(
        None, description="Instagram URL", examples=["https://instagram.com/store"]
    )
    footer_link_youtube: str | None = Field(None, description="YouTube URL")
    footer_link_x: str | None = Field(None, description="X (Twitter) URL")
    footer_link_tiktok: str | None = Field(None, description="TikTok URL")
    footer_signature_copy_1: NullableStr = Field(
        None, description="First line of footer signature. Null = use translated default.", examples=["Pozdrawiamy,"]
    )
    footer_signature_copy_2: NullableStr = Field(
        None, description="Second line of footer signature, rendered next to brand link", examples=["Ekipa"]
    )
    footer_socials_copy: NullableStr = Field(
        None, description="Copy displayed before social links", examples=["Obserwuj nas:"]
    )
    footer_automatic_copy: NullableStr = Field(
        None,
        description="Plain-text disclaimer at the bottom of the email. Newlines are converted to <br> on render.",
        examples=["To jest wiadomość automatyczna. Prosimy na nią nie odpowiadać."],
    )
    footer_unsubscribe_label: NullableStr = Field(
        None, description="Label for the unsubscribe link", examples=["Wypisz się"]
    )


class LangChannelConfigListResponse(BaseModel):
    count: int = Field(description="Total number of configs", examples=[3], ge=0)
    next: str | None = Field(None, description="Next page URL")
    previous: str | None = Field(None, description="Previous page URL")
    results: list[LangChannelConfigResponse] = Field(description="Config list")
