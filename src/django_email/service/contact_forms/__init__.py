"""Contact-forms email services.

All subclasses share the same ``prepare_context`` body — it lives on
``_ContactFormEmailBase`` to prevent drift. Submission-shaped emails (admin
notification + client copy) also share ``send()``; it lives on the base too,
parameterized by the ``template`` class attribute. Subclasses declare
``EMAIL_NAME``, ``model_class``, ``get_subject()``, and either ``template``
(to reuse the shared send) or their own ``send()`` (booking emails, which take
a different payload).
"""

from django_email.domain import EmailDomain
from django_email.service import EmailService
from django_email.template import EmailTemplate


class _ContactFormEmailBase(EmailService):
    """Shared ``prepare_context`` (+ submission-shaped ``send``) for contact-forms emails."""

    #: TemplateList member rendered by the shared ``send`` — set by submission-shaped subclasses.
    template: str | None = None

    def prepare_context(self, payload: dict) -> dict:
        ctx = {"subject": self.get_subject(), **payload}
        ctx.update(self.channel.variables_as_dict(self.language))
        if self.model:
            ctx.update(self.model.subject_as_dict())
            ctx.update(self.model.variables_as_dict())
        return ctx

    def send(self, email: list[str], submission_context: dict, attachment_rows: list | None = None) -> None:
        """Render + send a submission-shaped email to ``email``.

        ``attachment_rows`` accepts django-contact-forms' ``ContactFormAttachment``
        ORM rows — converted to ``EmailDomain.Attachment`` here so callers never
        import django-email internals. Rows without a file are skipped.
        """
        context = self.prepare_context(submission_context)
        message, html_message = EmailTemplate(template=self.template, context=context).render()
        subject = context.get("subject", self.get_subject())

        attachments = [
            EmailDomain.Attachment.from_path(row.attachment.path, display_name=row.name or None)
            for row in (attachment_rows or [])
            if row and row.attachment
        ]

        if attachments:
            self.domain.send_email_with_attachments(
                subject=subject, recipient_list=email, html_message=html_message, attachments=attachments
            )
        else:
            self.domain.send_email(subject=subject, message=message, recipient_list=email, html_message=html_message)
