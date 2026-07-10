# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Email service for resending voucher code (admin BOK action)."""

from datetime import datetime
from decimal import Decimal

from django.utils.translation import gettext as _

from django_email.models import CheckoutVoucher
from django_email.service import EmailService
from django_email.template import EmailTemplate


class VoucherResendEmailService(EmailService):
    EMAIL_NAME = "VOUCHER_RESEND"
    model: CheckoutVoucher
    model_class = CheckoutVoucher

    def get_subject(self) -> str:
        return _("Your voucher (resent)")

    def prepare_context(
        self,
        *,
        code: str,
        pin: str | None,
        expires_at: datetime,
        balance: Decimal,
        currency: str,
        voucher_id: int,
    ) -> dict:
        ctx = {
            "subject": self.get_subject(),
            "code": code,
            "pin": pin,
            "expires_at": expires_at,
            "balance": str(balance),
            "currency": currency,
            "voucher_id": voucher_id,
        }
        ctx.update(self.channel.variables_as_dict(self.language))
        if self.model:
            ctx.update(self.model.subject_for(CheckoutVoucher.KIND_RESEND))
            ctx.update(self.model.variables_as_dict())
        return ctx

    def send(
        self,
        email: list[str],
        *,
        code: str,
        pin: str | None,
        expires_at: datetime,
        balance: Decimal,
        currency: str,
        voucher_id: int,
    ) -> None:
        ctx = self.prepare_context(
            code=code,
            pin=pin,
            expires_at=expires_at,
            balance=balance,
            currency=currency,
            voucher_id=voucher_id,
        )
        message, html_message = EmailTemplate(template=EmailTemplate.TemplateList.VOUCHER_RESEND, context=ctx).render()
        self.domain.send_email(subject=ctx["subject"], message=message, recipient_list=email, html_message=html_message)
