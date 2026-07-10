# Email Brand Templates

Brand-neutral starting point for per-client email header/footer customization.

## How it works

Django template resolution with `APP_DIRS: True`:
1. `TEMPLATES[0]['DIRS']` — searched first (project-level)
2. App `templates/` dirs — searched in INSTALLED_APPS order

If your service adds `templates/base/header.html`, Django finds it before django-email's version.

## Setup (one-time per client service)

1. Copy base templates to your service:
   ```bash
   cp -r __email_brand.example/base/ /path/to/service/templates/base/
   ```

2. Ensure `TEMPLATES[0]['DIRS']` includes your service templates dir:
   ```python
   TEMPLATES = [{
       'DIRS': [os.path.join(BASE_DIR, 'templates')],
       # ...
   }]
   ```

3. Customize `templates/base/header.html` and `templates/base/footer.html` per client branding.

## Customization points

Both templates use Django template variables from `Channel.variables_as_dict()` and `LangChannelConfig.variables_as_dict()`:

### Channel variables (branding)
- `{{ main_bgc }}` — main background color (default: #FFFFFF)
- `{{ body_bgc }}` — body background color (default: #EDEDED)
- `{{ main_text_clr }}` — main text color (default: #141414)
- `{{ brand_text_clr }}` — brand text color (default: #404040)
- `{{ font_family }}` — CSS font family (default: 'Inter', sans-serif)
- `{{ logo_max_width }}` — logo max width in px (default: 100)

### LangChannelConfig variables (per-language)
- `{{ shop_name }}` — store display name
- `{{ logo_url }}` — logo image URL
- `{{ header_mail }}` — support email shown in header
- `{{ footer_copy }}` — footer text copy
- `{{ footer_name_brand }}` — brand name in footer
- `{{ footer_link_brand }}` — brand URL in footer
- `{{ footer_link_fb }}` — Facebook URL
- `{{ footer_link_ig }}` — Instagram URL
- `{{ footer_link_yt }}` — YouTube URL
- `{{ footer_link_x }}` — X (Twitter) URL
- `{{ footer_link_tiktok }}` — TikTok URL

## Fallback behavior

If you remove the client override, Django falls back to the module's built-in templates.
