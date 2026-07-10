# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from dataclasses import dataclass

from django.utils.translation import gettext as _

from django_email.dto import DTO
from django_email.models import CheckoutVirtualProduct
from django_email.service import EmailService
from django_email.template import EmailTemplate


class VirtualProductEmail(EmailService):
    EMAIL_NAME = "ORDER_VIRTUAL_COMPLETE"
    model: CheckoutVirtualProduct
    model_class = CheckoutVirtualProduct

    @dataclass
    class Product(DTO):
        name: str
        key: str
        additional_key: str | None = None

    @dataclass
    class Instruction(DTO):
        name: str
        content: str

    def get_subject(self) -> str:
        return _("Order Complete")

    def prepare_context(
        self, username: str, order_id: str, products: list[Product], instructions: list[Instruction]
    ) -> dict:
        default_context = {"subject": self.get_subject(), "products": products, "instructions": instructions}
        default_context.update(self.channel.variables_as_dict(self.language))
        if self.model:
            default_context.update(self.model.subject_as_dict(order_id))
            default_context.update(self.model.variables_as_dict(username, order_id))
        return default_context

    def send(
        self,
        email: list[str],
        username: str,
        order_id: str,
        products: list[Product],
        instructions: list[Instruction] = None,
    ):
        instructions = instructions or []
        context = self.prepare_context(username, order_id, products, instructions)
        message, html_message = EmailTemplate(
            template=EmailTemplate.TemplateList.VIRTUAL_PRODUCT, context=context
        ).render()

        self.domain.send_email(
            subject=context["subject"], message=message, recipient_list=email, html_message=html_message
        )
