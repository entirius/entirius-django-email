# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext as _

from django_email.domain import EmailDomain
from django_email.models import ReturnsReturnConfirmation
from django_email.service import EmailService
from django_email.template import EmailTemplate


class ReturnConfirmationEmail(EmailService):
    EMAIL_NAME = "RETURN_CONFIRMATION"
    model: ReturnsReturnConfirmation
    model_class = ReturnsReturnConfirmation

    def get_subject(self) -> str:
        return _("Return Confirmation")

    def prepare_context(
        self,
        first_name: str,
        last_name: str,
        customer_name: str,
        customer_username: str,
        customer_email: str,
        return_id: str,
        order_id: str,
        order_pretty_id: str,
        shop_shipping_address: str,
        comment: str = None,
    ) -> dict:
        username = (
            first_name + " " + last_name
            if first_name and last_name
            else (customer_name if customer_name else customer_username if customer_username else customer_email)
        )
        default_context = {
            "subject": self.get_subject(),
            "username": username,
            "return_id": return_id,
            "order_id": order_id,
            "comment": comment if comment else "",
            "order_pretty_id": order_pretty_id,
            "shipping_address": shop_shipping_address,
        }
        default_context.update(self.channel.variables_as_dict(self.language))
        if self.model:
            default_context.update(self.model.subject_as_dict())
            default_context.update(self.model.variables_as_dict(username, order_pretty_id, return_id))
        return default_context

    def build_attachment(self, path: str, name: str, ext: str) -> EmailDomain.Attachment:
        return EmailDomain.Attachment(path=path, name=name, ext=ext)

    def send(
        self,
        email: list[str],
        first_name: str,
        last_name: str,
        customer_name: str,
        customer_username: str,
        customer_email: str,
        return_id: str,
        order_id: str,
        order_pretty_id: str,
        shop_shipping_address: str,
        comment: str = None,
        attachments: [EmailDomain.Attachment] = None,
    ):
        context = self.prepare_context(
            first_name,
            last_name,
            customer_name,
            customer_username,
            customer_email,
            return_id,
            order_id,
            order_pretty_id,
            shop_shipping_address,
            comment,
        )
        message, html_message = EmailTemplate(
            template=EmailTemplate.TemplateList.RETURN_CONFIRMATION, context=context
        ).render()

        self.domain.send_email_with_attachments(
            subject=context.get("subject", self.get_subject()),
            recipient_list=email,
            html_message=html_message,
            attachments=attachments,
        )
