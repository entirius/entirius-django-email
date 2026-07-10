# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext as _

from django_email.models import ContactFormsBookingConfirmation
from django_email.service.contact_forms import _ContactFormEmailBase
from django_email.template import EmailTemplate

GREETING_PLACEHOLDER = "|booker_name|"


class BookingConfirmationEmail(_ContactFormEmailBase):
    EMAIL_NAME = "BOOKING_CONFIRMATION"
    model: ContactFormsBookingConfirmation
    model_class = ContactFormsBookingConfirmation

    def get_subject(self) -> str:
        return _("Your booking is confirmed")

    def prepare_context(self, payload: dict) -> dict:
        ctx = super().prepare_context(payload)
        greeting = ctx.get("greeting_template")
        if greeting and GREETING_PLACEHOLDER in greeting:
            booker_name = ctx.get("booker_name") or ""
            if not booker_name:
                self.logger.warning(
                    "greeting_template uses %s placeholder but booker_name is empty", GREETING_PLACEHOLDER
                )
            ctx["greeting_template"] = greeting.replace(GREETING_PLACEHOLDER, str(booker_name))
        return ctx

    def send(self, email: list[str], booking_context: dict) -> None:
        context = self.prepare_context(booking_context)
        message, html_message = EmailTemplate(
            template=EmailTemplate.TemplateList.BOOKING_CONFIRMATION, context=context
        ).render()
        self.domain.send_email(
            subject=context.get("subject", self.get_subject()),
            message=message,
            recipient_list=email,
            html_message=html_message,
        )
