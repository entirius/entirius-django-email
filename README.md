# django-email

Transactional email for Volkanos — branded, per-channel and per-language email templates with
an admin API. Ships email services for account, checkout, loyalty, returns and newsletter flows.

## Installation

```shell
pip install entirius-django-email
```

Add the app to your project:

```python
INSTALLED_APPS = [
    ...
    "django_regional",
    "django_email",
]
```

## Brand templates

Header/footer branding is resolved through Django template precedence: put your brand overrides in
a project-level template directory (see `__email_brand.example/`) — app defaults apply otherwise.

## Development

```shell
make install     # sync dependencies (uv)
make check       # lint + format check (ruff)
make test        # test suite (pytest + pytest-django)
```

Development and agent instructions: [AGENTS.md](AGENTS.md).

## License

Mozilla Public License 2.0 — see [LICENSE](LICENSE).
