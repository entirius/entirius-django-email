# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Central registry of email types.

The keys are the ``EMAIL_NAME`` identifiers declared on each ``EmailService``
subclass. They are the stable, send-time identifier used to decide whether a
BCC copy should be dispatched for a given email (see
``Channel.get_bcc_recipients`` and ``Channel.bcc_email_types``).
"""

from django.utils.translation import gettext_lazy as _

# (EMAIL_NAME, human readable label) -- order drives the admin widget order.
EMAIL_TYPE_CHOICES: list[tuple[str, str]] = [
    ("SIGNUP_CONFIRMATION", _("Accounts — new account")),
    ("PASSWORD_RESET_CONFIRMATION", _("Accounts — reset password")),
    ("ORDER_VIRTUAL_COMPLETE", _("Checkout — virtual product")),
    ("CHECKOUT_INVOICE", _("Checkout — invoice")),
    ("COUPON_CONFIRMATION", _("Loyalty — coupon confirmation")),
    ("RETURN_CONFIRMATION", _("Returns — return confirmation")),
    ("ALLEGRO_ORDER_VIRTUAL_COMPLETE", _("Allegro — virtual product")),
    ("NEWSLETTER_SIGNUP_CONFIRMATION", _("Agreements — newsletter signup")),
    ("BOOKING_CONFIRMATION", _("Contact forms — booking confirmation")),
    ("BOOKING_ADMIN_NOTIFICATION", _("Contact forms — booking admin notification")),
    ("CONTACT_FORM_SUBMISSION", _("Contact forms — submission")),
]

EMAIL_TYPE_KEYS: set[str] = {key for key, _label in EMAIL_TYPE_CHOICES}
