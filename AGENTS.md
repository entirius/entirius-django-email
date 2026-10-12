# AGENTS.md

`entirius-django-email` (Django app `django_email`) — transactional email module of Entirius. Branded, per-channel and per-language email templates
with an admin API and ready-made email services for platform flows.

## Commands

| Command | Meaning |
|---|---|
| `make install` | sync dependencies (uv, incl. extras) |
| `make check` | lint + format-check (ruff) |
| `make fix` | auto-fix lint + format |
| `make test` | test suite (pytest + pytest-django) |

## Conventions

- English only: code, docs, commits, branches, PRs.
- MPL-2.0: every non-trivial source file carries the license header (pre-commit inserts it).
- Toolchain: uv + ruff + hatchling + pytest; all config in `pyproject.toml`; `uv.lock` committed.
- Git flow: `master` (production) + `develop` (integration); changes land via PR; semver tag on `master`.
- Never rename the package / Django app_label / DB table prefix `django_email` — it is a schema contract.
- Migrations are part of the public contract — never edit an already released migration.
- Access: areas live on the AppConfig (`access_areas`, `access_route_rules`), every admin view carries
  `access_area`; a new admin route without one fails `tests/test_access_ownership.py`.
- Default: do not commit — git is the user's call.
- No AI attribution in commits or PR descriptions.

## Architecture

- `models/` — `Channel` (branding: colors, fonts, sender info), `LangChannelConfig` (per-language
  overrides), per-flow email log models under `accounts/`, `checkout/`, `loyalty/`, `returns/`,
  `allegro/`, `agreements/`.
- `service/` — `EmailService` abstract base + concrete implementations per flow
  (new account, reset password, virtual product, coupon confirmation, return confirmation,
  newsletter signup).
- `services/` — API service layer: channel, lang-config and template services.
- `api/v2/` — admin API (JWT + IsAdminUser; read + update only) under `api/email/v2/admin/`.
- `templates/` + `__email_brand.example/` — base templates; brand overrides resolve through
  project-level template dirs (`APP_DIRS` precedence).
- `language.py` — `resolve_email_language()` fallback chain (requested → channel default).
- `checks.py` — configuration health checks, registered in `AppConfig.ready()`.
- `management/commands/test-email.py` — sends a test email for a channel.

| Topic | Where |
|---|---|
| Overview, email types, language and sender resolution | `docs/index.md` |
| Settings, per-channel SMTP, template paths, test command | `docs/configuration.md` |
| Admin API endpoints and examples | `docs/admin-api.md` |
| Brand template overrides | `docs/template-theming.md`, `__email_brand.example/README.md` |
| CMS email panel | `docs/cms-panel.md` |
| ERD config and generated diagrams | `docs/erd-config.yaml`, `docs/erd.md` |

## Settings

Read in `src/django_email/settings.py`; the `*_EMAIL_TEMPLATE_PATH` settings (one per email type) are listed in
`docs/configuration.md`.

| Setting | Default | Description |
|---|---|---|
| `AVAILABLE_LANGUAGES` | `["en", "pl"]` | Languages the email services accept (read as `EMAIL_AVAILABLE_LANGUAGES`) |
| `EMAIL_DEFAULT_LANGUAGE` | `"pl"` | Fallback when the requested language is not available |
| `DEFAULT_FROM_EMAIL` | `None` | Global sender, used when the channel sets none |
| `EMAIL_ADMIN_API_ENABLED` | `True` | `False` leaves the admin API unmounted and its DRF / pydantic imports untouched |
| `EMAIL_SMTP_CONFIGURATION_CHANNELS` | `None` | Per-channel SMTP settings keyed by channel idx |

## Gotchas

- Email sending is synchronous SMTP via Django email backend — callers wrap in try/except;
  consumers (e.g. agreements) treat this module as optional.
- `LangChannelConfig.language = None` is the channel-default row — always present per channel.
