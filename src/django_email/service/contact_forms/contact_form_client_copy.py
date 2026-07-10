# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext as _

from django_email.models import ContactFormsClientCopy
from django_email.service.contact_forms import _ContactFormEmailBase
from django_email.template import EmailTemplate


class ContactFormClientCopyEmail(_ContactFormEmailBase):
    """Confirmation copy sent to the submitter (customer), distinct from the
    admin notification. Reuses the submission context (and the shared
    ``_ContactFormEmailBase.send``) so the customer sees a copy of what they
    sent, under client-facing copy ("thank you")."""

    EMAIL_NAME = "CONTACT_FORM_CLIENT_COPY"
    model: ContactFormsClientCopy
    model_class = ContactFormsClientCopy
    template = EmailTemplate.TemplateList.CONTACT_FORM_CLIENT_COPY

    def get_subject(self) -> str:
        return _("Thank you for contacting us")
