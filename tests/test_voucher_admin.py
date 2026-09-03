# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for the CheckoutVoucher admin registration.

Voucher email copy is edited in Django admin like every other flow, so the model
has to reach the default admin site and its changelist columns have to be fields
Django can actually render.
"""

from django.contrib import admin

from django_email.models import CheckoutVoucher


def test_voucher_model_is_registered_on_the_admin_site():
    assert admin.site.is_registered(CheckoutVoucher)


def test_voucher_changelist_columns_pass_admin_checks():
    assert admin.site.get_model_admin(CheckoutVoucher).check() == []
