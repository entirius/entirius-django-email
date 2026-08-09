---
title: "Admin API"
description: "v2 admin API for managing email channels, language configs, and templates."
---

The email module exposes a v2 admin API for reading and updating channel configuration, language configs, and email templates. Create and delete operations are Django admin only.

## Base URL

```
/api/email/v2/admin/<shop_idx>/
```

## Authentication

All endpoints require JWT authentication with admin permissions.

```
Authorization: Bearer <token>
```

Obtain a token from `/api/token/`. The authenticated user must be `is_staff` or `is_superuser`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `channels/` | List email channels |
| `GET` | `channels/<idx>/` | Retrieve channel by idx |
| `PATCH` | `channels/<idx>/` | Update channel branding and SMTP settings |
| `GET` | `channels/<idx>/lang-configs/` | List language configs for a channel |
| `GET` | `channels/<idx>/lang-configs/<lang>/` | Retrieve language config |
| `PATCH` | `channels/<idx>/lang-configs/<lang>/` | Update language config |
| `GET` | `channels/<idx>/templates/<slug>/` | List templates for a channel and email type |
| `GET` | `channels/<idx>/templates/<slug>/<lang>/` | Retrieve template |
| `PATCH` | `channels/<idx>/templates/<slug>/<lang>/` | Update template content |

Full interactive reference is available at `/api/docs/` (Swagger UI) when the service is running.

## Email Type Slugs

The `<slug>` path parameter maps to email type models:

| Slug | Model | Description |
|------|-------|-------------|
| `new-account` | `AccountsNewAccount` | Account registration confirmation |
| `reset-password` | `AccountsResetPassword` | Password reset link |
| `virtual-product` | `CheckoutVirtualProduct` | Digital product delivery |
| `coupon-confirmation` | `LoyaltyCouponConfirmation` | Loyalty coupon issued |
| `return-confirmation` | `ReturnsReturnConfirmation` | Return request received |
| `allegro-virtual-product` | `AllegroVirtualProduct` | Allegro digital product delivery |
| `newsletter-signup` | `AgreementsNewsletterSignup` | Newsletter subscription confirmation |

## get_or_create Behavior on PATCH

`PATCH /channels/<idx>/templates/<slug>/<lang>/` creates the template record if it does not exist. This means operators can activate a language for a channel by patching a template — no separate "create" step is needed.

The response always returns the full template object, whether it was created or updated.

## Example: Update Template Subject and Body

```bash
curl -X PATCH \
  "http://localhost:8000/api/email/v2/admin/example/channels/default/templates/new-account/en/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Welcome to our store",
    "welcome": "Hi {{username}}, your account is ready."
  }'
```

## Example: Update Channel Branding

```bash
curl -X PATCH \
  "http://localhost:8000/api/email/v2/admin/example/channels/default/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "from_name": "My Store",
    "from_email": "noreply@mystore.com",
    "main_background_color": "#1A1C25",
    "body_background_color": "#F5F5F5"
  }'
```

## Notes

- No create or delete endpoints — add new channels and template records via Django admin.
- Channel `idx` values must match PIM Channel `idx` values for correct routing.
- Language codes use ISO2 format (`en`, `pl`, `de`).
- Template fields are email-type specific — see the Swagger UI for field lists per slug.
