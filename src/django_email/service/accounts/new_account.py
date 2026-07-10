# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext as _

from django_email.models import AccountsNewAccount
from django_email.service import EmailService
from django_email.template import EmailTemplate


class NewAccountEmail(EmailService):
    EMAIL_NAME = "SIGNUP_CONFIRMATION"
    model: AccountsNewAccount
    model_class = AccountsNewAccount

    def get_subject(self) -> str:
        return _("Signup Confirmation")

    def prepare_context(self, username: str, confirmation_link: str) -> dict:
        default_context = {"subject": self.get_subject(), "username": username, "confirmation_link": confirmation_link}
        default_context.update(self.channel.variables_as_dict(self.language))
        if self.model:
            default_context.update(self.model.subject_as_dict())
            default_context.update(self.model.variables_as_dict(username))
        return default_context

    def send(self, email: list[str], username: str, confirmation_link: str):
        context = self.prepare_context(username, confirmation_link)
        message, html_message = EmailTemplate(template=EmailTemplate.TemplateList.NEW_ACCOUNT, context=context).render()

        self.domain.send_email(
            subject=context.get("subject", self.get_subject()),
            message=message,
            recipient_list=email,
            html_message=html_message,
        )
