# entirius-django-email

A Django module for transactional email in Entirius, the open-source modular ecommerce platform: branded templates per sales channel and language.
It ships ready-made email services for account, checkout, loyalty, returns, newsletter and contact-form flows, and an
admin API for editing branding and templates.

[![PyPI](https://img.shields.io/pypi/v/entirius-django-email.svg)](https://pypi.org/project/entirius-django-email/)
[![Python](https://img.shields.io/pypi/pyversions/entirius-django-email.svg)](https://pypi.org/project/entirius-django-email/)
[![License: MPL-2.0](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](https://github.com/entirius/entirius-django-email/blob/develop/LICENSE)

## What it does

- Sends transactional emails through ready-made services, one per flow (new account, password reset, virtual
  product, voucher, return confirmation, newsletter signup, booking and contact-form messages).
- Stores branding per sales channel (colors, fonts, sender) with per-language overrides.
- Resolves the email language with a fallback chain: requested language, then the channel default.
- Lets a project override header and footer templates without forking the module (see `__email_brand.example/`).
- Routes mail through per-channel SMTP settings when `EMAIL_SMTP_CONFIGURATION_CHANNELS` is set.
- Exposes an admin API under `api/email/v2/admin/` for channels, language configs and templates.

## Installation

```shell
uv add entirius-django-email
pip install entirius-django-email
```

```python
INSTALLED_APPS = [
    ...
    "django_utils",
    "django_regional",
    "django_email",
]

# urls.py
urlpatterns = [
    path("", include("django_email.urls")),
]
```

Optional settings: `AVAILABLE_LANGUAGES`, `EMAIL_DEFAULT_LANGUAGE`, `DEFAULT_FROM_EMAIL`, `EMAIL_ADMIN_API_ENABLED`,
`EMAIL_SMTP_CONFIGURATION_CHANNELS`; reference with defaults in
https://github.com/entirius/entirius-django-email/blob/develop/docs/configuration.md.

## Quick start

```python
from django_email.service.accounts.new_account import NewAccountEmail

# channel_idx names an existing django_email Channel row
NewAccountEmail(language="en", channel_idx="default").send(
    email=["customer@example.com"],
    username="Ada",
    confirmation_link="https://shop.example.com/confirm/abc",
)
```

## Requirements

- Python 3.11 or newer, Django 4.0 or newer.
- Django REST Framework, `djangorestframework-simplejwt`, `pydantic`, `drf-spectacular` (admin API).
- An SMTP server reachable through the Django email backend.
- Entirius packages pulled in: `entirius-django-utils`, `entirius-django-regional`, `entirius-py-process-logger`.

## Documentation

- Module docs: https://github.com/entirius/entirius-django-email/tree/develop/docs
- Entirius documentation: https://docs.entirius.com/
- Changelog: https://github.com/entirius/entirius-django-email/blob/develop/CHANGELOG.md

## Part of Entirius

This module runs inside the Entirius backend service (Volkanos); the modules that own a flow call its email services.

- Backend service: https://github.com/entirius/entirius-service-volkanos
- Docker harness: https://github.com/entirius/entirius-zeno
- Sibling modules: https://github.com/entirius/entirius-django-accounts, https://github.com/entirius/entirius-django-regional, https://github.com/entirius/entirius-django-utils

## Development

```shell
make install     # sync dependencies (uv)
make check       # lint + format check (ruff)
make test        # test suite (pytest + pytest-django)
```

Development and agent instructions: https://github.com/entirius/entirius-django-email/blob/develop/AGENTS.md

## License

Mozilla Public License 2.0 (MPL-2.0) — see https://github.com/entirius/entirius-django-email/blob/develop/LICENSE.
