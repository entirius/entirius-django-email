# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.contrib import admin
from django_utils.admin.base_admin import BaseModelAdmin as ModelAdmin

from django_email.models import LoyaltyCouponConfirmation


@admin.register(LoyaltyCouponConfirmation)
class LoyaltyCouponConfirmationAdmin(ModelAdmin):
    list_display = ("channel", "language", "subject")
    list_display_links = list_display
