# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pydantic import BaseModel, ConfigDict, Field


class ChannelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    idx: str = Field(description="Channel identifier", examples=["default-europe"])
    label: str = Field(description="Display name", examples=["Default Europe"])
    from_name: str | None = Field(None, description="Sender display name", examples=["My Store"])
    from_email: str | None = Field(None, description="Sender email address", examples=["noreply@store.com"])
    from_t9n: dict | None = Field(
        None,
        description="Per-language sender override JSON",
        examples=[{"en": {"from_name": "Store", "from_email": "en@store.com"}}],
    )
    main_background_color: str = Field(description="Main background hex color", examples=["#FFFFFF"])
    body_background_color: str = Field(description="Body background hex color", examples=["#EDEDED"])
    main_text_color: str = Field(description="Main text hex color", examples=["#141414"])
    brand_text_color: str = Field(description="Brand text hex color", examples=["#404040"])
    font_family: str = Field(description="CSS font-family value", examples=["'Inter', sans-serif"])
    logo_max_width: str = Field(description="Logo max width in pixels", examples=["100"])


class ChannelListResponse(BaseModel):
    count: int = Field(description="Total number of channels", examples=[2], ge=0)
    next: str | None = Field(None, description="Next page URL")
    previous: str | None = Field(None, description="Previous page URL")
    results: list[ChannelResponse] = Field(description="Channel list")
