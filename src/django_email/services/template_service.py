# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models
from django.db.models import Model, QuerySet
from django_utils.api.exceptions import NotFound

from django_email.models import (
    AccountsNewAccount,
    AccountsResetPassword,
    AgreementsNewsletterSignup,
    AllegroVirtualProduct,
    CheckoutVirtualProduct,
    ContactFormsBookingAdminNotification,
    ContactFormsBookingConfirmation,
    ContactFormsSubmission,
    LoyaltyCouponConfirmation,
    ReturnsReturnConfirmation,
)

EMAIL_TYPE_MODELS: dict[str, type] = {
    "accounts-new-account": AccountsNewAccount,
    "accounts-reset-password": AccountsResetPassword,
    "checkout-virtual-product": CheckoutVirtualProduct,
    "loyalty-coupon-confirmation": LoyaltyCouponConfirmation,
    "returns-return-confirmation": ReturnsReturnConfirmation,
    "allegro-virtual-product": AllegroVirtualProduct,
    "agreements-newsletter-signup": AgreementsNewsletterSignup,
    "contact-forms-booking-confirmation": ContactFormsBookingConfirmation,
    "contact-forms-booking-admin-notification": ContactFormsBookingAdminNotification,
    "contact-forms-submission": ContactFormsSubmission,
}


def _resolve_model(email_type: str) -> type:
    model_class = EMAIL_TYPE_MODELS.get(email_type)
    if not model_class:
        raise NotFound(f"Unknown email type: {email_type}")
    return model_class


def list_templates(email_type: str, shop_idx: str) -> QuerySet:
    model_class = _resolve_model(email_type)
    return model_class.objects.filter(channel__idx=shop_idx).select_related("language")


def get_template(email_type: str, pk: int, shop_idx: str) -> Model:
    model_class = _resolve_model(email_type)
    try:
        return model_class.objects.get(pk=pk, channel__idx=shop_idx)
    except model_class.DoesNotExist:
        raise NotFound("Template not found") from None


def update_template(email_type: str, pk: int, shop_idx: str, **fields: object) -> Model:
    model_class = _resolve_model(email_type)
    try:
        instance = model_class.objects.get(pk=pk, channel__idx=shop_idx)
    except model_class.DoesNotExist:
        raise NotFound("Template not found") from None
    # Coerce None to "" on non-nullable string columns so the CMS can clear a field
    # by sending null without violating the DB constraint. Nullable columns keep null
    # as a meaningful value (matches existing pattern for AccountsNewAccount-style models).
    for field, value in fields.items():
        if value is None:
            model_field = model_class._meta.get_field(field)
            if not model_field.null and isinstance(model_field, (models.CharField, models.TextField)):
                value = ""
        setattr(instance, field, value)
    instance.save()
    return instance
