# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.urls import include, path

from django_email import settings

urlpatterns = []

if settings.EMAIL_ADMIN_API_ENABLED:
    urlpatterns.append(path("api/email/v2/admin/", include("django_email.api.v2.urls")))
