# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext as _

from django_email.models import ContactFormsSubmission
from django_email.service.contact_forms import _ContactFormEmailBase
from django_email.template import EmailTemplate


class ContactFormSubmissionEmail(_ContactFormEmailBase):
    EMAIL_NAME = "CONTACT_FORM_SUBMISSION"
    model: ContactFormsSubmission
    model_class = ContactFormsSubmission
    template = EmailTemplate.TemplateList.CONTACT_FORM_SUBMISSION

    def get_subject(self) -> str:
        return _("New contact form submission")
