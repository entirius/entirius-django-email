# Changelog

## 4.0.1 — 2026-07-22

- Extend the squash `replaces` list to cover a late upstream leaf migration,
  so existing databases cut over cleanly.

## 4.0.0 — 2026-07-10

- Initial public release: transactional email templating and delivery —
  channel-branded, multilingual templates with operator-editable copy per
  channel and language.
- Admin API v2 (JWT + IsAdminUser): read and update for channels, language
  configs, and templates.
- Email services consumed by accounts, checkout, returns, agreements
  (newsletter signup), and contact-forms (booking confirmation, admin
  notification, submission).
- `django_email.language.resolve_email_language(requested, channel)` — the
  canonical language-resolution helper for all senders.
- Template theming: per-deployment HTML/text overrides via a brand directory
  in `TEMPLATES[0]['DIRS']`.
- Explicit `Meta.app_label` on every model, so consumers can import from
  `django_email.models` even when the app is absent from test settings.
- Migrations squashed into a single initial migration for the Entirius epoch.
