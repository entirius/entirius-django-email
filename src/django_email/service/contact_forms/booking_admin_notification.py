# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext as _

from django_email.models import ContactFormsBookingAdminNotification
from django_email.service.contact_forms import _ContactFormEmailBase
from django_email.template import EmailTemplate


class BookingAdminNotificationEmail(_ContactFormEmailBase):
    EMAIL_NAME = "BOOKING_ADMIN_NOTIFICATION"
    model: ContactFormsBookingAdminNotification
    model_class = ContactFormsBookingAdminNotification

    def get_subject(self) -> str:
        return _("New booking")

    def send(self, email: list[str], booking_context: dict) -> None:
        context = self.prepare_context(booking_context)
        message, html_message = EmailTemplate(
            template=EmailTemplate.TemplateList.BOOKING_ADMIN_NOTIFICATION, context=context
        ).render()
        self.domain.send_email(
            subject=context.get("subject", self.get_subject()),
            message=message,
            recipient_list=email,
            html_message=html_message,
        )
