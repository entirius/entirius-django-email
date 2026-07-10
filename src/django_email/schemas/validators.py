# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Shared Pydantic validators for django-email schemas."""

import re
from typing import Annotated

from pydantic import BeforeValidator

# Matches HTML that's structurally non-empty but visually blank — what BasicWysiwyg
# emits for an empty editor: <p></p>, <p><br></p>, <p>&nbsp;</p>, plus whitespace-only.
_EMPTY_WYSIWYG_RE = re.compile(
    r"^\s*(?:<p>(?:\s|&nbsp;|<br\s*/?>)*</p>\s*)+$",
    re.IGNORECASE,
)


def strip_empty_wysiwyg(value: str | None) -> str | None:
    """Coerce empty-but-non-blank WYSIWYG HTML to None.

    Treats `<p></p>`, `<p><br></p>`, `<p>&nbsp;</p>`, and any combination of
    those as empty (returns None). Real content passes through unchanged.
    """
    if value is None:
        return None
    if not value.strip():
        return None
    if _EMPTY_WYSIWYG_RE.match(value):
        return None
    return value


# Use as a request-schema field type for any WYSIWYG-backed column. Empty editor
# output (<p></p>, <p><br></p>, etc.) is normalized to None before reaching the
# service layer; the service then coerces None to "" for non-nullable columns.
WysiwygStr = Annotated[str | None, BeforeValidator(strip_empty_wysiwyg)]
