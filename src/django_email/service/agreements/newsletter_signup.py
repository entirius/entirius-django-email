# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext as _

from django_email.models.agreements.newsletter_signup import AgreementsNewsletterSignup
from django_email.service import EmailService
from django_email.template import EmailTemplate


class NewsletterSignupEmail(EmailService):
    EMAIL_NAME = "NEWSLETTER_SIGNUP_CONFIRMATION"
    model: AgreementsNewsletterSignup
    model_class = AgreementsNewsletterSignup

    def get_subject(self) -> str:
        return _("Newsletter Signup Confirmation")

    def prepare_context(self, confirmation_link: str, username: str = None) -> dict:
        default_context = {"subject": self.get_subject(), "confirmation_link": confirmation_link}
        if username:
            default_context["username"] = username
        default_context.update(self.channel.variables_as_dict(self.language))
        if self.model:
            default_context.update(self.model.subject_as_dict())
            default_context.update(self.model.variables_as_dict(username))
        return default_context

    def send(self, email: list[str], confirmation_link: str, username: str = None, unsubscribe_url: str | None = None):
        context = self.prepare_context(confirmation_link, username)
        if unsubscribe_url:
            context["unsubscribe_url"] = unsubscribe_url
        message, html_message = EmailTemplate(
            template=EmailTemplate.TemplateList.NEWSLETTER_SIGNUP, context=context
        ).render()
        extra_headers = None
        if unsubscribe_url:
            extra_headers = {
                "List-Unsubscribe": f"<{unsubscribe_url}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            }
        self.domain.send_email(
            subject=context.get("subject", self.get_subject()),
            message=message,
            recipient_list=email,
            html_message=html_message,
            extra_headers=extra_headers,
        )
