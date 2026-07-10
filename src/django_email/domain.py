# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from smtplib import SMTPException, SMTPServerDisconnected

from django.core import mail
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django_utils.api.exceptions import BadRequest
from process_logger import ProcessLoggerMixin

from django_email import settings


class EmailDomain(ProcessLoggerMixin):
    class ExceptionType:
        BACKEND = "BACKEND"
        API = "API"

    class ExceptionMessage:
        def smtp(self, e):
            return f"Błąd SMTP: {e}. Make sure your config have right encryption EMAIL_USE_TLS/EMAIL_USE_SSL"

    class Attachment:
        path: str
        name: str
        ext: str

        def __init__(self, path: str, name: str, ext: str):
            self.path = path
            self.name = name
            self.ext = ext

        @classmethod
        def from_path(cls, path: str, display_name: str | None = None) -> "EmailDomain.Attachment":
            """Build an Attachment from a filesystem path + optional display name.

            Strips CR/LF/control characters from ``display_name`` — Django's mail
            backend escapes MIME headers, but this is belt-and-braces defence
            against header injection via a user-uploaded filename.
            Files without an extension keep ``ext=""`` (not ``"bin"`` — that
            misrepresents plain-text uploads).
            """
            import os
            import re

            raw_name = display_name or os.path.basename(path)
            raw_name = re.sub(r"[\r\n\x00-\x1f\x7f]", "", raw_name)
            name, _, ext = raw_name.rpartition(".")
            return cls(path=path, name=(name or raw_name), ext=ext)

    exception_type: str
    _from_email: str = None
    _bcc: list[str] = None

    def __init__(self, exception_type: str = ExceptionType.BACKEND, channel_idx: str = None):
        self.exception_type = exception_type
        self.channel_idx = channel_idx
        self.channel_smtp_connection = self.get_channel_smtp_connection_if_exists()
        self.add_send_mail = {}
        if self.channel_smtp_connection:
            self.add_send_mail = {"connection": self.channel_smtp_connection}

    def set_from_email(self, from_email: str):
        self._from_email = from_email

    def set_bcc(self, bcc: list[str]):
        """Set the blind carbon copy recipients applied to every send on this domain."""
        self._bcc = bcc or None

    def get_from_email(self):
        if self._from_email:
            return self._from_email
        else:
            return settings.DEFAULT_FROM_EMAIL

    def _raise_exception_by_type(self, e, status=None, message=None):
        self.logger.exception(e)
        match self.exception_type:
            case self.ExceptionType.BACKEND:
                raise e
            case self.ExceptionType.API:
                params = {}
                if status:
                    params["status"] = status
                if message:
                    params["message"] = message
                raise BadRequest(**params)

    def get_channel_smtp_connection_if_exists(self):
        if settings.EMAIL_SMTP_CONFIGURATION_CHANNELS:
            channel_smtp_config = settings.EMAIL_SMTP_CONFIGURATION_CHANNELS.get(self.channel_idx, None)
            if channel_smtp_config:
                try:
                    return get_connection(
                        host=channel_smtp_config["EMAIL_HOST"],
                        port=channel_smtp_config["EMAIL_PORT"],
                        username=channel_smtp_config["EMAIL_HOST_USER"],
                        password=channel_smtp_config["EMAIL_HOST_PASSWORD"],
                        use_ssl=channel_smtp_config["EMAIL_USE_SSL"],
                        use_tls=channel_smtp_config["EMAIL_USE_TLS"],
                    )
                except Exception as e:
                    self.logger.exception(f"Error getting channel {self.channel_idx} SMTP settings: {e}")
                    return None
        return None

    def send_email(
        self,
        subject: str,
        message: str,
        recipient_list: list[str],
        html_message: str = None,
        extra_headers: dict[str, str] | None = None,
    ):
        try:
            self.logger.add_log_param_once("subject", subject)
            self.logger.add_log_param_once("recipient_list", recipient_list)
            from_email = self.get_from_email()
            self.logger.add_log_param_once("from_email", from_email)
            if extra_headers:
                connection = self.channel_smtp_connection or None
                email_msg = EmailMessage(
                    subject=subject,
                    body=html_message or message,
                    from_email=from_email,
                    to=recipient_list,
                    bcc=self._bcc,
                    headers=extra_headers,
                    connection=connection,
                )
                email_msg.content_subtype = "html"
                email_msg.send(fail_silently=False)
            elif self._bcc:
                email_msg = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=from_email,
                    to=recipient_list,
                    bcc=self._bcc,
                    connection=self.channel_smtp_connection or None,
                )
                if html_message:
                    email_msg.attach_alternative(html_message, "text/html")
                email_msg.send(fail_silently=False)
            else:
                mail.send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=recipient_list,
                    fail_silently=False,
                    html_message=html_message,
                    **self.add_send_mail,
                )
            self.logger.info(f"Email sent with subject {subject} to {str(recipient_list)}")

        except SMTPServerDisconnected as e:
            self._raise_exception_by_type(e, status="FAIL", message=self.ExceptionMessage().smtp(e))
        except SMTPException as e:
            self._raise_exception_by_type(e, status="FAIL", message=self.ExceptionMessage().smtp(e))
        except Exception as e:
            self._raise_exception_by_type(e)

    def _build_html_message(self, subject: str, html_message: str, recipient_list: list[str]) -> EmailMessage:
        email_message = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=self.get_from_email(),
            to=recipient_list,
            bcc=self._bcc,
            connection=self.channel_smtp_connection,
        )
        email_message.content_subtype = "html"
        return email_message

    def _send_with_smtp_handling(self, email_message: EmailMessage, subject: str, recipient_list: list[str]) -> None:
        self.logger.add_log_param_once("subject", subject)
        self.logger.add_log_param_once("recipient_list", recipient_list)
        try:
            email_message.send(fail_silently=False)
            self.logger.info(f"Email sent with subject {subject} to {str(recipient_list)}")
        except SMTPServerDisconnected as e:
            self._raise_exception_by_type(e, status="FAIL", message=self.ExceptionMessage().smtp(e))
        except SMTPException as e:
            self._raise_exception_by_type(e, status="FAIL", message=self.ExceptionMessage().smtp(e))
        except Exception as e:
            self._raise_exception_by_type(e)

    def send_email_with_attachments(
        self, subject: str, recipient_list: list[str], html_message: str = None, attachments: list[Attachment] = None
    ):
        email_message = self._build_html_message(subject, html_message, recipient_list)
        for attachment in attachments or []:
            with open(attachment.path, "rb") as file:
                email_message.attach(f"{attachment.name}.{attachment.ext}", file.read(), "application/octet-stream")
        self._send_with_smtp_handling(email_message, subject, recipient_list)

    def send_email_with_bytes_attachment(
        self,
        subject: str,
        recipient_list: list[str],
        html_message: str,
        attachment_content: bytes,
        attachment_filename: str,
        attachment_mimetype: str,
    ):
        email_message = self._build_html_message(subject, html_message, recipient_list)
        email_message.attach(attachment_filename, attachment_content, attachment_mimetype)
        self._send_with_smtp_handling(email_message, subject, recipient_list)
