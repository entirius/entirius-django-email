---
title: "Template Theming"
description: "Per-client email template override system — logos, colors, and footer text without forking module templates."
---

`django-email` ships default HTML and text templates inside each owning module (`django_accounts`, `django_checkout`, etc.). The theming system lets you override header and footer visuals per client without modifying module code.

## How It Works

Django's template engine resolves templates by searching `TEMPLATES[0]['DIRS']` before `APP_DIRS`. Place a client-specific directory in `DIRS` and Django uses it when the path matches — otherwise the module default is used.

```
Django template resolution order:
1. TEMPLATES[0]['DIRS'] — client override directory (checked first)
2. APP_DIRS — module bundled templates (fallback)
```

## Directory Layout

The override directory is named `__email_brand.{client}/` and lives inside the service repo:

```
{client}-volkanos/
└── __email_brand.{client}/
    └── django_email/
        └── base/
            ├── header.html
            ├── header.txt
            ├── footer.html
            └── footer.txt
```

All email templates extend the shared base header and footer. Overriding these two files changes the visual wrapper for every email type.

## Client Setup

**Step 1:** Create the override directory in the service repo:

```bash
mkdir -p __email_brand.myclient/django_email/base/
```

**Step 2:** Copy the default header and footer from `django-email`:

```bash
# From inside the service repo
cp .venv/lib/python3.11/site-packages/django_email/templates/django_email/base/header.html \
   __email_brand.myclient/django_email/base/header.html
cp .venv/lib/python3.11/site-packages/django_email/templates/django_email/base/footer.html \
   __email_brand.myclient/django_email/base/footer.html
# Repeat for .txt variants
```

**Step 3:** Add the directory to `TEMPLATES[0]['DIRS']` in `settings.py`:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "__email_brand.myclient",
        ],
        "APP_DIRS": True,
        # ...
    }
]
```

**Step 4:** Edit the copied templates. Customization points:

| File | What to change |
|------|----------------|
| `header.html` | Logo image URL, banner background color, header link |
| `footer.html` | Footer text, social links, brand name, unsubscribe link |
| `header.txt` | Plain text shop name and URL |
| `footer.txt` | Plain text footer copy |

## Customization Points

Inside `header.html`, the logo and primary color are the main targets:

```html
<!-- Logo -->
<img src="{{ logo_url }}" alt="{{ shop_name }}" width="160" />

<!-- Primary color — background of header banner -->
<table style="background-color: {{ main_background_color }};">
```

`logo_url` and `shop_name` come from `LangChannelConfig` for the current channel and language. `main_background_color` and `body_background_color` come from `Channel`.

Set these values in Django admin under Email > Channels and Email > Language Channel Configs, or via the [Admin API](./admin-api/).

## Fallback Behavior

If no override directory is in `DIRS`, or if the override directory does not contain the template file, Django falls through to the module-bundled default. You can override selectively — for example, override only the footer and leave the header as the module default.

## Contact-Forms Integration

`django-contact-forms` uses the shared email header/footer automatically when `EmailDomain` is passed to the contact form service. No additional template setup is needed — the same `__email_brand.{client}/` directory covers contact form emails too.

## Verifying the Override

Use the test-email command to confirm the override is active before deploying:

```bash
python manage.py test-email my-channel test@example.com new_account --lang en
```

Check that the output email uses the client logo and footer, not the module defaults.
