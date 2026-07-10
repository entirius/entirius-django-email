# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pydantic import BaseModel, Field


class ChannelUpdateRequest(BaseModel):
    from_name: str | None = Field(None, description="Sender display name", examples=["My Store"])
    from_email: str | None = Field(None, description="Sender email", examples=["noreply@store.com"])
    from_t9n: dict | None = Field(None, description="Per-language sender override JSON")
    main_background_color: str | None = Field(None, description="Main background hex color", examples=["#FFFFFF"])
    body_background_color: str | None = Field(None, description="Body background hex color", examples=["#EDEDED"])
    main_text_color: str | None = Field(None, description="Main text hex color", examples=["#141414"])
    brand_text_color: str | None = Field(None, description="Brand text hex color", examples=["#404040"])
    font_family: str | None = Field(None, description="CSS font-family value", examples=["'Inter', sans-serif"])
    logo_max_width: str | None = Field(None, description="Logo max width in px", examples=["100"])
