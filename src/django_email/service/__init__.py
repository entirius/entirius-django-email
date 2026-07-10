from abc import ABC

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import activate
from django_regional.models import Language
from process_logger import ProcessLogger, ProcessLoggerMixin

from django_email.domain import EmailDomain
from django_email.models import Channel
from django_email.settings import EMAIL_AVAILABLE_LANGUAGES, EMAIL_DEFAULT_LANGUAGE


class EmailService(ProcessLoggerMixin, ABC):
    class ExceptionType:
        BACKEND = "BACKEND"
        API = "API"

    EMAIL_NAME = None
    domain: EmailDomain
    language: str
    django_regional_language: Language
    channel: Channel
    model: object
    model_class = None

    def __init__(self, exception_type: str = ExceptionType.BACKEND, language: str = None, channel_idx: str = None):
        self.domain = EmailDomain(exception_type, channel_idx)
        self.logger = ProcessLogger("DJANGO_EMAIL")
        self.domain.set_logger(self.logger)
        self.logger.add_log_param_once("email", self.EMAIL_NAME)
        self._activate_language(language)
        self.channel = Channel.objects.filter(idx=channel_idx).first() if channel_idx else None
        self._set_from_email_from_channel()
        if not self.channel:
            raise ValueError("Channel is not set")
        self.domain.set_bcc(self.channel.get_bcc_recipients(self.EMAIL_NAME))
        try:
            self.model = self.model_class.objects.get(channel=self.channel, language__iso2=self.language)
        except ObjectDoesNotExist:
            self.model = self.model_class(channel=self.channel, language=self.django_regional_language)

    def _activate_language(self, language: str):
        if language in EMAIL_AVAILABLE_LANGUAGES:
            self.language = language
        else:
            self.language = EMAIL_DEFAULT_LANGUAGE
        self.logger.add_log_param_once("language", self.language)
        activate(self.language)
        try:
            self.django_regional_language = Language.objects.get(iso2=self.language)
        except Language.DoesNotExist:
            self.logger.warning(f"django_regional Language {self.language} not found")

    def _set_from_email_from_channel(self):
        if self.channel:
            if self.channel.from_t9n and self.channel.from_t9n.get(self.language, {}).get("from_email"):
                from_email = self.channel.from_t9n.get(self.language).get("from_email")
                if self.channel.from_t9n.get(self.language).get("from_name"):
                    from_name = self.channel.from_t9n.get(self.language).get("from_name")
                    self.domain.set_from_email(f"{from_name} <{from_email}>")
                else:
                    self.domain.set_from_email(from_email)
            elif self.channel.from_email:
                if self.channel.from_name:
                    self.domain.set_from_email(f"{self.channel.from_name} <{self.channel.from_email}>")
                else:
                    self.domain.set_from_email(self.channel.from_email)

    def set_from_email(self, from_email: str):
        self.domain.set_from_email(from_email)

    def get_subject(self) -> str:
        raise NotImplementedError

    def prepare_context(self, **kwargs) -> dict:
        raise NotImplementedError

    def send(self, **kwargs):
        raise NotImplementedError
