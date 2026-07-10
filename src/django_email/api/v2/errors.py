# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Error helpers for v2 API views.

Mirrors the pattern from django-contact-forms `utils/v2_errors.py` so the v2
exception handler can format Pydantic errors into the structured `{ error,
message, debug_id, details[] }` response that the CMS `useFormErrors`
composable parses for field-level error display.

Local helper rather than cross-module import to keep django-email standalone.
"""

from pydantic import ValidationError as PydanticValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


def raise_pydantic_as_drf(exc: PydanticValidationError) -> None:
    detail: dict[str, list[str]] = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"]) or "non_field_errors"
        detail.setdefault(field, []).append(error["msg"])
    raise DRFValidationError(detail)
