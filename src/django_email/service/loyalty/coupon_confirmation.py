# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext as _

from django_email.models import LoyaltyCouponConfirmation
from django_email.service import EmailService
from django_email.template import EmailTemplate


class CouponConfirmationEmail(EmailService):
    EMAIL_NAME = "COUPON_CONFIRMATION"
    model: LoyaltyCouponConfirmation
    model_class = LoyaltyCouponConfirmation

    def get_subject(self) -> str:
        return _("Coupon Confirmation")

    def prepare_context(self, username: str, confirmation_link: str, loyalty_coupon: str) -> dict:
        default_context = {
            "subject": self.get_subject(),
            "username": username,
            "confirmation_link": confirmation_link,
            "loyalty_coupon": loyalty_coupon,
        }
        default_context.update(self.channel.variables_as_dict(self.language))
        if self.model:
            default_context.update(self.model.subject_as_dict())
            default_context.update(self.model.variables_as_dict(username))
        return default_context

    def send(self, email: list[str], username: str, confirmation_link: str, loyalty_coupon: str):
        context = self.prepare_context(username, confirmation_link, loyalty_coupon)
        message, html_message = EmailTemplate(
            template=EmailTemplate.TemplateList.COUPON_CONFIRMATION, context=context
        ).render()

        self.domain.send_email(
            subject=context.get("subject", self.get_subject()),
            message=message,
            recipient_list=email,
            html_message=html_message,
        )
