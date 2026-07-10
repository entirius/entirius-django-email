# AGENTS.md

Transactional email module for Volkanos — distribution `entirius-django-email`,
Django app `django_email`. Branded, per-channel and per-language email templates
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
- Default: do not commit — git is the user's call.

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

## Gotchas

- Email sending is synchronous SMTP via Django email backend — callers wrap in try/except;
  consumers (e.g. agreements) treat this module as optional.
- `LangChannelConfig.language = None` is the channel-default row — always present per channel.
