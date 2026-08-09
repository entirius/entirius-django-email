---
title: "Email"
description: "Transactional email templating and delivery for accounts, checkout, and returns."
sidebar:
  label: "Overview"
  collapsed: true
---

`django-email` handles transactional email for the Volkanos platform. Other modules call its services to send templated, channel-branded, multilingual emails. Operators manage template content via the CMS Email panel or the v2 admin API.

## Key Concepts

- **Channel** — branding configuration (colors, fonts, logo, sender identity). Each channel can have its own SMTP server and per-language sender name/address.
- **LangChannelConfig** — per-language overrides for a channel (shop name, logo URL, footer text).
- **Email Templates** — model-based email content. Each email type has a dedicated model with subject and body fields, linked to a channel and language.
- **EmailService** — abstract base class. Concrete services handle language activation, sender resolution (channel → per-language override → `DEFAULT_FROM_EMAIL`), context preparation, and delivery via `EmailDomain`.
- **EmailDomain** — handles SMTP dispatch. Selects the channel-specific SMTP connection if configured, falls back to the global backend.

## Email Types

| Email Type | Model | Service | Called By |
|---|---|---|---|
| New Account | `AccountsNewAccount` | `NewAccountEmail` | django-accounts |
| Password Reset | `AccountsResetPassword` | `ResetPasswordEmail` | django-accounts |
| Virtual Product | `CheckoutVirtualProduct` | `VirtualProductEmail` | django-checkout |
| Coupon Confirmation | `LoyaltyCouponConfirmation` | `CouponConfirmationEmail` | django-loyalty |
| Return Confirmation | `ReturnsReturnConfirmation` | `ReturnConfirmationEmail` | django-returns |
| Allegro Virtual Product | `AllegroVirtualProduct` | `AllegroVirtualProductEmail` | django-allegro |
| Newsletter Signup | `AgreementsNewsletterSignup` | `NewsletterSignupEmail` | django-agreements |
| Booking Confirmation | `ContactFormsBookingConfirmation` | `BookingConfirmationEmail` | django-contact-forms |
| Booking Admin Notification | `ContactFormsBookingAdminNotification` | `BookingAdminNotificationEmail` | django-contact-forms |
| Contact Form Submission | `ContactFormsSubmission` | `ContactFormSubmissionEmail` | django-contact-forms |

## Language Resolution

All `EmailService` subclasses share the same language-resolution contract — documented once in `django_email.language.resolve_email_language(requested_iso2, channel)`:

1. Explicit `requested_iso2` wins when truthy (schema-validated caller input)
2. Falls back to `channel.default_language.iso2`
3. Falls back to `EMAIL_DEFAULT_LANGUAGE` inside `EmailService._activate_language` (silent — never a 4xx)

Callers in django-contact-forms and django-agreements import this helper rather than reimplementing the chain. The contact-forms multilang pattern (booker language vs admin channel-default) is covered in the contact-forms module docs.

## Sender Resolution

`EmailService` resolves the `from_email` in this order:

1. Per-language `from_email` from `Channel.from_t9n[lang]`
2. Channel-level `Channel.from_email` / `Channel.from_name`
3. `DEFAULT_FROM_EMAIL` setting

## Admin API (v2)

The v2 admin API exposes read and update operations for email channels, language configs, and templates. Create and delete are Django admin only.

- **Base URL:** `/api/email/v2/admin/<shop_idx>/`
- **Auth:** JWT + IsAdminUser
- **Full reference:** [Admin API](./admin-api/)

## Template Theming

Per-client template overrides live in `__email_brand.{client}/` inside the service repo. Django's template resolution picks up overrides automatically — no settings change needed if the directory is in `TEMPLATES[0]['DIRS']`.

See [Template Theming](./template-theming/) for client setup instructions.

## CMS Panel

The CMS Email panel lets operators edit template text content, sender branding, and language configs without developer access. See [CMS Panel](./cms-panel/) for panel navigation and usage.

## Related Modules

- **[Accounts](/volkanos/modules/accounts/)** — calls `NewAccountEmail` and `ResetPasswordEmail`
- **[Agreements](/volkanos/modules/agreements/)** — calls `NewsletterSignupEmail`
- **[Contact Forms](/volkanos/modules/contact-forms/)** — uses shared email header/footer with optional `EmailDomain`
- **[Database Diagrams](./erd/)** — auto-generated ER diagrams for all Email models
