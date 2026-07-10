# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext as _

from django_email.models import CheckoutInvoice
from django_email.service import EmailService
from django_email.template import EmailTemplate


class InvoiceEmail(EmailService):
    EMAIL_NAME = "CHECKOUT_INVOICE"
    model: CheckoutInvoice
    model_class = CheckoutInvoice

    def get_subject(self) -> str:
        return _("Invoice for your order")

    def prepare_context(self, username: str, order_id: str) -> dict:
        context = {"subject": self.get_subject()}
        context.update(self.channel.variables_as_dict(self.language))
        if self.model:
            context.update(self.model.subject_as_dict(order_id))
            context.update(self.model.variables_as_dict(username, order_id))
        return context

    def send(self, email: list[str], username: str, order_id: str, invoice_pdf: bytes, invoice_filename: str) -> None:
        context = self.prepare_context(username, order_id)
        _, html_message = EmailTemplate(template=EmailTemplate.TemplateList.CHECKOUT_INVOICE, context=context).render()

        self.domain.send_email_with_bytes_attachment(
            subject=context["subject"],
            recipient_list=email,
            html_message=html_message,
            attachment_content=invoice_pdf,
            attachment_filename=invoice_filename,
            attachment_mimetype="application/pdf",
        )
