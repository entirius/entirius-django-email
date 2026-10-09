# Changelog

## [Unreleased]

- Access: the module declares its own access areas on its AppConfig and its admin views (copied from the
  entirius-django-access defaults; behaviour unchanged).

## 4.1.0 — 2026-09-30

- **Fix:** `EmailDomain` built without `set_logger` (django-communicator, django-notifications) no longer raises
  `AttributeError` on an incomplete `EMAIL_SMTP_CONFIGURATION_CHANNELS` entry — it logs through the module logger
  and reports no channel connection.
- **SMTP health.** `django_email.services.smtp_status`: `smtp_status(channel_idx)` (settings only) and
  `smtp_probe(channel_idx)` (one SMTP login, cached 60 s, never raises → `configured | unconfigured |
  unreachable | auth_failed`). System checks `email.smtp`: an incomplete `EMAIL_SMTP_CONFIGURATION_CHANNELS`
  entry — a key missing, or an empty `EMAIL_HOST` / `EMAIL_PORT` (tag `entirius_config`), and the login probe (tag `entirius_probe`, deploy-only). Shown by
  django-munin's `health/` endpoint.

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
