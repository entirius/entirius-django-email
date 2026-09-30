---
title: "CMS Email Panel"
description: "Operator guide for managing email templates and channel configuration in the CMS."
---

The CMS Email panel lets operators edit email template content, sender branding, and per-language configuration without developer access. Creating or deleting channels and template records requires Django admin.

## Navigation

In the CMS, open the **Emails** panel from the sidebar. The panel has four sections:

| Section | What it shows |
|---------|---------------|
| Dashboard | All configured email channels |
| Channel Edit | Branding settings for one channel |
| Language Config Edit | Per-language overrides for a channel |
| Template List | All email types for a channel |
| Template Edit | Subject and body fields for one email type and language |

## Dashboard

Lists all email channels configured in the system. Each card shows the channel name, sender address, and a count of configured languages. Click a channel to open Channel Edit.

## Channel Edit

Edit the visual and sender settings that apply to all emails sent through this channel:

| Field | Description |
|-------|-------------|
| From Name | Sender display name (e.g., "My Store") |
| From Email | Global sender address (fallback when no per-language override exists) |
| Main Background Color | Header banner background (hex color) |
| Body Background Color | Email body background (hex color) |

Changes apply to all email types on this channel. Per-language sender overrides are in Language Config Edit.

## Language Config Edit

Override channel settings for a specific language:

| Field | Description |
|-------|-------------|
| Shop Name | Used in email header and subject lines |
| Logo URL | URL to the client logo image shown in the header |
| Header Mail | Contact email address shown in the header |
| Footer Copy | Copyright line at the bottom of every email |
| Footer Name Brand | Brand name used in footer text |

If a field is empty, the channel-level value or module default is used.

## Template List

Shows all 7 email types for the selected channel. Each row shows the type name and which languages have been configured. Click an email type to open Template Edit.

Email types that have not been configured for a language show "Not configured". Opening Template Edit for an unconfigured language creates the record automatically on save.

## Template Edit

Edit the text content for one email type in one language. Fields vary by email type — for example, `new_account` has `subject`, `welcome`, `announce`, `confirm_button`, and `thank_you`, while `reset_password` has `subject`, `welcome`, `reset_button`, and `help`.

**What operators can edit:**
- Subject line and all body text fields
- All supported languages (switch language via the language selector)

**What operators cannot do via the CMS panel:**
- Create new channels or delete existing ones (Django admin only)
- Configure SMTP credentials (settings file only)
- Change template HTML structure (requires [Template Theming](./template-theming/))
- Add new email types (requires a new module version)

## Template Variables

Template text fields support variables in `{{variable}}` format. Available variables differ per email type — hover over a field label in the CMS to see the available variables list, or check the Swagger UI for the full field schema.

Common variables across all types:
- `{{username}}` — recipient's display name
- `{{shop_name}}` — from `LangChannelConfig.shop_name`
- `{{logo_url}}` — from `LangChannelConfig.logo_url`
