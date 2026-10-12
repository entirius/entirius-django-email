# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext as _

from django_email.models import ContactFormsSubmission
from django_email.service.contact_forms import _ContactFormEmailBase
from django_email.template import EmailTemplate

FORM_ID_PLACEHOLDER = "<contact_form_id>"


class ContactFormSubmissionEmail(_ContactFormEmailBase):
    EMAIL_NAME = "CONTACT_FORM_SUBMISSION"
    model: ContactFormsSubmission
    model_class = ContactFormsSubmission
    template = EmailTemplate.TemplateList.CONTACT_FORM_SUBMISSION

    def get_subject(self) -> str:
        """Shipped default. Carries the placeholder so a channel with no operator-set
        subject still gets one mail thread per submission — a constant subject makes
        Gmail collapse every notification into a single conversation."""
        return f"{_('New contact form submission')} #{FORM_ID_PLACEHOLDER}"

    def prepare_context(self, payload: dict) -> dict:
        ctx = super().prepare_context(payload)
        ctx["subject"] = self._resolve_form_id(ctx["subject"], payload.get("form_id"))
        return ctx

    def _resolve_form_id(self, subject: str, form_id: str | None) -> str:
        """Expand ``<contact_form_id>`` to the submission id. No placeholder, no id —
        an operator who wants the old threading behaviour just leaves it out."""
        if FORM_ID_PLACEHOLDER not in subject:
            return subject
        if not form_id:
            self.logger.warning(f"Subject uses {FORM_ID_PLACEHOLDER} but the caller sent no form_id")
        return subject.replace(FORM_ID_PLACEHOLDER, str(form_id or "")).strip()
