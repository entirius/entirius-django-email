# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext as _

from django_email.models import AccountsResetPassword
from django_email.service import EmailService
from django_email.template import EmailTemplate


class ResetPasswordEmail(EmailService):
    EMAIL_NAME = "PASSWORD_RESET_CONFIRMATION"
    model: AccountsResetPassword
    model_class = AccountsResetPassword

    def get_subject(self) -> str:
        return _("Password Reset Confirmation")

    def prepare_context(self, confirmation_link: str) -> dict:
        default_context = {"subject": self.get_subject(), "confirmation_link": confirmation_link}
        default_context.update(self.channel.variables_as_dict(self.language))
        if self.model:
            default_context.update(self.model.subject_as_dict())
            default_context.update(self.model.variables_as_dict())
        return default_context

    def send(self, email: list[str], confirmation_link: str):
        context = self.prepare_context(confirmation_link)
        message, html_message = EmailTemplate(
            template=EmailTemplate.TemplateList.RESET_PASSWORD, context=context
        ).render()

        self.domain.send_email(
            subject=context.get("subject", self.get_subject()),
            message=message,
            recipient_list=email,
            html_message=html_message,
        )
