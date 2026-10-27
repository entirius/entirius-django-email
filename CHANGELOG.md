# Changelog

## 4.3.0 — 2026-10-27

- Contact-form submission subject (`ContactFormsSubmission.subject`) understands `<contact_form_id>`, substituted with
  the `form_id` the caller sends, so every notification gets its own mail thread (Gmail threads by subject). The
  shipped default subject is `New contact form submission #<contact_form_id>`; an operator-set subject without the
  token stays as it is. A caller that sends no `form_id` gets the token (and a `#` in front of it) dropped, with a
  warning in the log. Migration `0018` changes only the field's `help_text`; the column is unchanged.
- The contact-form submission and client-copy templates render `form_body_rows` (a list of `label` / `value` items)
  as one table row per field, multi-line values through `linebreaksbr`. A caller that sends only `form_body` gets the
  old `<pre>` block. django-contact-forms 4.1.0 sends both, and `form_id`.
- `EmailService.send_prerendered(email, *, subject, html_message, message)` sends a body the caller has already
  rendered, wrapped in `base/prerendered_body.html` (the shared header, footer and channel variables). The HTML is
  inserted unescaped: the caller sanitises anything user-supplied in it. `message` is the text/plain part.
- Django admin: `CheckoutVoucher` is registered (it was the only checkout email model missing).
- Tests cover the `EMAIL_ADMIN_API_ENABLED` URL toggle.

## 4.2.0 — 2026-10-12

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
