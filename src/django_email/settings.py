# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.conf import settings

EMAIL_AVAILABLE_LANGUAGES = getattr(settings, "AVAILABLE_LANGUAGES", ["en", "pl"])
EMAIL_DEFAULT_LANGUAGE = getattr(settings, "EMAIL_DEFAULT_LANGUAGE", "pl")

DEFAULT_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", None)

# ADMIN API v2 — when False, the admin API is not mounted in urls.py and its
# DRF / pydantic / drf-spectacular imports are never triggered (safe for services
# that do not install those packages). Enabled by default.
EMAIL_ADMIN_API_ENABLED = getattr(settings, "EMAIL_ADMIN_API_ENABLED", True)

# NEW_ACCOUNT
NEW_ACCOUNT_EMAIL_TEMPLATE_PATH = getattr(
    settings, "NEW_ACCOUNT_EMAIL_TEMPLATE_PATH", "django_accounts/email/default_new_account"
)

# RESET_PASSWORD
RESET_PASSWORD_EMAIL_TEMPLATE_PATH = getattr(
    settings, "RESET_PASSWORD_EMAIL_TEMPLATE_PATH", "django_accounts/email/default_pass_reset"
)

# RETURN_CONFIRMATION
RETURN_CONFIRMATION_EMAIL_TEMPLATE_PATH = getattr(
    settings, "RETURN_CONFIRMATION_EMAIL_TEMPLATE_PATH", "django_returns/email/default_return"
)

# COUPON_CONFIRMATION
COUPON_CONFIRMATION_EMAIL_TEMPLATE_PATH = getattr(
    settings, "COUPON_CONFIRMATION_EMAIL_TEMPLATE_PATH", "django_loyalty/email/default_get_coupon"
)

# VIRTUAL_PRODUCT
VIRTUAL_PRODUCT_EMAIL_TEMPLATE_PATH = getattr(
    settings, "VIRTUAL_PRODUCT_EMAIL_TEMPLATE_PATH", "django_checkout/email/default_virtual_product"
)

# CHECKOUT_INVOICE
CHECKOUT_INVOICE_EMAIL_TEMPLATE_PATH = getattr(
    settings, "CHECKOUT_INVOICE_EMAIL_TEMPLATE_PATH", "django_checkout/email/default_invoice"
)

# VOUCHER (3 email types share the same model_class CheckoutVoucher)
VOUCHER_ISSUED_ON_PURCHASE_EMAIL_TEMPLATE_PATH = getattr(
    settings,
    "VOUCHER_ISSUED_ON_PURCHASE_EMAIL_TEMPLATE_PATH",
    "django_checkout/email/default_voucher_issued_on_purchase",
)
VOUCHER_ISSUED_BY_ADMIN_EMAIL_TEMPLATE_PATH = getattr(
    settings,
    "VOUCHER_ISSUED_BY_ADMIN_EMAIL_TEMPLATE_PATH",
    "django_checkout/email/default_voucher_issued_by_admin",
)
VOUCHER_RESEND_EMAIL_TEMPLATE_PATH = getattr(
    settings,
    "VOUCHER_RESEND_EMAIL_TEMPLATE_PATH",
    "django_checkout/email/default_voucher_resend",
)

# ALLEGRO_VIRTUAL_PRODUCT
ALLEGRO_VIRTUAL_PRODUCT_EMAIL_TEMPLATE_PATH = getattr(
    settings, "ALLEGRO_VIRTUAL_PRODUCT_EMAIL_TEMPLATE_PATH", "django_allegro/email/default_virtual_product"
)


# NEWSLETTER_SIGNUP
NEWSLETTER_SIGNUP_EMAIL_TEMPLATE_PATH = getattr(
    settings, "NEWSLETTER_SIGNUP_EMAIL_TEMPLATE_PATH", "django_agreements/email/default_newsletter_signup"
)

# CONTACT_FORMS — BOOKING_CONFIRMATION
BOOKING_CONFIRMATION_EMAIL_TEMPLATE_PATH = getattr(
    settings, "BOOKING_CONFIRMATION_EMAIL_TEMPLATE_PATH", "django_contact_forms/email/booking_confirmation"
)

# CONTACT_FORMS — BOOKING_ADMIN_NOTIFICATION
BOOKING_ADMIN_NOTIFICATION_EMAIL_TEMPLATE_PATH = getattr(
    settings, "BOOKING_ADMIN_NOTIFICATION_EMAIL_TEMPLATE_PATH", "django_contact_forms/email/booking_admin_notification"
)

# CONTACT_FORMS — CONTACT_FORM_SUBMISSION (generic)
CONTACT_FORM_SUBMISSION_EMAIL_TEMPLATE_PATH = getattr(
    settings, "CONTACT_FORM_SUBMISSION_EMAIL_TEMPLATE_PATH", "django_contact_forms/email/contact_form_submission"
)

# CONTACT_FORMS — CONTACT_FORM_CLIENT_COPY (copy to the submitter)
CONTACT_FORM_CLIENT_COPY_EMAIL_TEMPLATE_PATH = getattr(
    settings, "CONTACT_FORM_CLIENT_COPY_EMAIL_TEMPLATE_PATH", "django_contact_forms/email/contact_form_client_copy"
)


# EMAIL_SMTP_CONFIGURATION_CHANNELS = {"channel_idx_1": {
#     "EMAIL_PORT": ""
#     "EMAIL_HOST": ""
#     "EMAIL_HOST_USER": ""
#     "EMAIL_HOST_PASSWORD": ""
#     "EMAIL_USE_SSL": ""
#     "EMAIL_USE_TLS": ""
#     "DEFAULT_FROM_EMAIL": ""
# }}

EMAIL_SMTP_CONFIGURATION_CHANNELS = getattr(settings, "EMAIL_SMTP_CONFIGURATION_CHANNELS", None)
