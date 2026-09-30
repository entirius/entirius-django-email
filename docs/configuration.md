---
title: "Configuration"
description: "Email settings, SMTP configuration, template paths, Mailpit dev setup, and the test-email command."
---

## Settings

| Setting | Default | Description |
|---|---|---|
| `EMAIL_AVAILABLE_LANGUAGES` | `["en", "pl"]` (from `AVAILABLE_LANGUAGES`) | Languages the email service will accept. Requests for unlisted languages fall back to `EMAIL_DEFAULT_LANGUAGE`. |
| `EMAIL_DEFAULT_LANGUAGE` | `"pl"` | Fallback language when the requested language is not in `EMAIL_AVAILABLE_LANGUAGES`. |
| `DEFAULT_FROM_EMAIL` | `None` (Django default) | Global sender address. Used when no channel-level sender is configured. |
| `EMAIL_SMTP_CONFIGURATION_CHANNELS` | `None` | Per-channel SMTP overrides. See below. Set to `None` in dev to disable per-channel routing and route everything through Mailpit. |
| `NEW_ACCOUNT_EMAIL_TEMPLATE_PATH` | `"django_accounts/email/default_new_account"` | Template path for new account emails. |
| `RESET_PASSWORD_EMAIL_TEMPLATE_PATH` | `"django_accounts/email/default_pass_reset"` | Template path for password reset emails. |
| `RETURN_CONFIRMATION_EMAIL_TEMPLATE_PATH` | `"django_returns/email/default_return"` | Template path for return confirmation emails. |
| `COUPON_CONFIRMATION_EMAIL_TEMPLATE_PATH` | `"django_loyalty/email/default_get_coupon"` | Template path for coupon confirmation emails. |
| `VIRTUAL_PRODUCT_EMAIL_TEMPLATE_PATH` | `"django_checkout/email/default_virtual_product"` | Template path for checkout virtual product emails. |
| `ALLEGRO_VIRTUAL_PRODUCT_EMAIL_TEMPLATE_PATH` | `"django_allegro/email/default_virtual_product"` | Template path for Allegro virtual product emails. |
| `NEWSLETTER_SIGNUP_EMAIL_TEMPLATE_PATH` | `"django_agreements/email/default_newsletter_signup"` | Template path for newsletter signup confirmation emails. |

## Per-Channel SMTP

Set `EMAIL_SMTP_CONFIGURATION_CHANNELS` to override SMTP settings per channel. When a channel's `idx` matches a key in this dict, its connection is used instead of the global Django email backend.

```python
EMAIL_SMTP_CONFIGURATION_CHANNELS = {
    "channel-idx-1": {
        "EMAIL_HOST": "smtp.example.com",
        "EMAIL_PORT": 587,
        "EMAIL_HOST_USER": "noreply@example.com",
        "EMAIL_HOST_PASSWORD": "secret",
        "EMAIL_USE_TLS": True,
        "EMAIL_USE_SSL": False,
        "DEFAULT_FROM_EMAIL": "noreply@example.com",
    },
    "channel-idx-2": {
        # ... separate SMTP for a second channel
    },
}
```

If the connection setup fails (wrong host, bad credentials), the error is logged and the channel falls back to the global backend.

`EMAIL_USE_TLS` and `EMAIL_USE_SSL` are mutually exclusive — set one to `True`, the other to `False`.

An entry must carry all six connection keys, with a non-empty `EMAIL_HOST` and `EMAIL_PORT` (an unset env var
arrives as `""`); an incomplete one falls back silently. Check it before the first send:

```bash
python manage.py check --tag email.smtp                      # incomplete entries (settings only)
python manage.py check --deploy --tag entirius_probe         # one SMTP login per complete entry
```

Some consumers have no fallback: django-communicator sends nothing for a channel without its entry and reports
that as `communicator.smtp`.

## Development Setup (Mailpit)

Use Mailpit as a local SMTP server to capture all outgoing emails without delivering them.

Add to `settings_local.py` (or Docker environment):

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mailpit"        # Docker service name; use "localhost" for bare-metal
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SMTP_CONFIGURATION_CHANNELS = None  # Disable per-channel routing in dev
```

Mailpit web UI is at `http://localhost:8025`. All emails sent by Django (regardless of channel) appear there.

In entirius-docker, Mailpit runs as the `mailpit` service. The `settings_local.py` injected during `make dev` configures Django to use it automatically.

## Template Paths

Templates follow Django's template engine resolution. The default paths point to templates bundled with the owning modules (`django_accounts`, `django_checkout`, etc.). Override a path to use a custom template:

```python
NEW_ACCOUNT_EMAIL_TEMPLATE_PATH = "myshop/email/new_account"
```

Each template path resolves to two files: `{path}.html` (HTML part) and `{path}.txt` (plain text fallback).

For per-client visual overrides (logo, colors, footer), use the template theming system instead of changing these paths. See [Template Theming](./template-theming/).

## Test Email Command

Send a test email for any type without triggering real business logic:

```bash
python manage.py test-email <channel_idx> <to_email> <type> [--lang ISO2]
```

`--lang` defaults to `pl`.

Supported types:

| Type | Service |
|---|---|
| `new_account` | `NewAccountEmail` |
| `reset_password` | `ResetPasswordEmail` |
| `coupon_confirmation` | `CouponConfirmationEmail` |
| `return_confirmation` | `ReturnConfirmationEmail` |
| `virtual_product` | `VirtualProductEmail` |
| `allegro_virtual_product` | `AllegroVirtualProductEmail` |
| `newsletter_signup` | `NewsletterSignupEmail` |

Example:

```bash
python manage.py test-email my-channel ops@example.com new_account --lang en
```

The command sends with dummy data (placeholder username, confirmation link, etc.) to verify SMTP config and template rendering without creating any database records.
