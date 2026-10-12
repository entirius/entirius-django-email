# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Unit tests for django-email service layer."""

import pytest
from django_utils.api.exceptions import NotFound

from django_email.services import channel_service, lang_config_service, template_service

from .factories import (
    AccountsNewAccountFactory,
    ChannelFactory,
    ContactFormsBookingAdminNotificationFactory,
    ContactFormsBookingConfirmationFactory,
    ContactFormsSubmissionFactory,
    LangChannelConfigFactory,
    _get_or_create_language,
)

# ---------------------------------------------------------------------------
# channel_service
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestChannelService:
    def test_list_channels_filters_by_shop_idx(self):
        # Arrange
        target = ChannelFactory(idx="shop-a")
        ChannelFactory(idx="shop-b")
        ChannelFactory(idx="shop-c")

        # Act
        result = channel_service.list_channels(shop_idx="shop-a")

        # Assert
        assert result.count() == 1
        assert result.first().pk == target.pk

    def test_list_channels_excludes_other_shops(self):
        # Arrange
        ChannelFactory(idx="shop-x")
        ChannelFactory(idx="shop-y")

        # Act
        result = channel_service.list_channels(shop_idx="shop-z")

        # Assert
        assert result.count() == 0

    def test_get_channel_returns_correct_instance(self):
        # Arrange
        channel = ChannelFactory()

        # Act
        result = channel_service.get_channel(pk=channel.pk, shop_idx=channel.idx)

        # Assert
        assert result.pk == channel.pk
        assert result.idx == channel.idx

    def test_get_channel_raises_not_found_for_wrong_pk(self):
        # Act / Assert
        with pytest.raises(NotFound):
            channel_service.get_channel(pk=999999, shop_idx="any")

    def test_get_channel_raises_not_found_for_wrong_shop(self):
        # Arrange
        channel = ChannelFactory(idx="shop-a")

        # Act / Assert
        with pytest.raises(NotFound):
            channel_service.get_channel(pk=channel.pk, shop_idx="shop-b")

    def test_update_channel_persists_color(self):
        # Arrange
        channel = ChannelFactory(main_background_color="#FFFFFF")

        # Act
        updated = channel_service.update_channel(pk=channel.pk, shop_idx=channel.idx, main_background_color="#123456")

        # Assert
        assert updated.main_background_color == "#123456"
        channel.refresh_from_db()
        assert channel.main_background_color == "#123456"

    def test_update_channel_partial_update_leaves_other_fields(self):
        # Arrange
        channel = ChannelFactory(from_name="Original", from_email="orig@test.com")

        # Act
        channel_service.update_channel(pk=channel.pk, shop_idx=channel.idx, from_name="Updated")

        # Assert
        channel.refresh_from_db()
        assert channel.from_name == "Updated"
        assert channel.from_email == "orig@test.com"

    def test_update_channel_raises_not_found(self):
        # Act / Assert
        with pytest.raises(NotFound):
            channel_service.update_channel(pk=999999, shop_idx="any", from_name="X")


# ---------------------------------------------------------------------------
# lang_config_service
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestLangConfigService:
    def test_list_lang_configs_filters_by_channel(self):
        # Arrange
        channel_a = ChannelFactory()
        channel_b = ChannelFactory()
        LangChannelConfigFactory(channel=channel_a)
        LangChannelConfigFactory(channel=channel_a, language="en")
        LangChannelConfigFactory(channel=channel_b)

        # Act
        result = lang_config_service.list_lang_configs(channel_pk=channel_a.pk)

        # Assert
        assert result.count() == 2
        for cfg in result:
            assert cfg.channel_id == channel_a.pk

    def test_get_lang_config_returns_correct_instance(self):
        # Arrange
        config = LangChannelConfigFactory()

        # Act
        result = lang_config_service.get_lang_config(pk=config.pk, shop_idx=config.channel.idx)

        # Assert
        assert result.pk == config.pk

    def test_get_lang_config_raises_not_found(self):
        # Act / Assert
        with pytest.raises(NotFound):
            lang_config_service.get_lang_config(pk=999999, shop_idx="any")

    def test_update_lang_config_persists_footer_copy(self):
        # Arrange
        config = LangChannelConfigFactory(footer_copy="Original footer")

        # Act
        updated = lang_config_service.update_lang_config(
            pk=config.pk, shop_idx=config.channel.idx, footer_copy="Updated footer"
        )

        # Assert
        assert updated.footer_copy == "Updated footer"
        config.refresh_from_db()
        assert config.footer_copy == "Updated footer"

    def test_update_lang_config_raises_not_found(self):
        # Act / Assert
        with pytest.raises(NotFound):
            lang_config_service.update_lang_config(pk=999999, shop_idx="any", footer_copy="X")


# ---------------------------------------------------------------------------
# template_service
# ---------------------------------------------------------------------------


EMAIL_TYPE = "accounts-new-account"


@pytest.mark.django_db
class TestTemplateService:
    def test_list_templates_filters_by_shop(self):
        # Arrange
        channel_a = ChannelFactory()
        channel_b = ChannelFactory()
        AccountsNewAccountFactory(channel=channel_a)
        AccountsNewAccountFactory(channel=channel_a)
        AccountsNewAccountFactory(channel=channel_b)

        # Act
        result = template_service.list_templates(email_type=EMAIL_TYPE, shop_idx=channel_a.idx)

        # Assert
        assert result.count() == 2

    def test_list_templates_returns_empty_for_unknown_shop(self):
        # Act
        result = template_service.list_templates(email_type=EMAIL_TYPE, shop_idx="nonexistent-shop")

        # Assert
        assert result.count() == 0

    def test_list_templates_raises_not_found_for_unknown_type(self):
        # Act / Assert
        with pytest.raises(NotFound):
            template_service.list_templates(email_type="unknown-type", shop_idx="any")

    def test_get_template_returns_correct_instance(self):
        # Arrange
        template = AccountsNewAccountFactory()

        # Act
        result = template_service.get_template(email_type=EMAIL_TYPE, pk=template.pk, shop_idx=template.channel.idx)

        # Assert
        assert result.pk == template.pk

    def test_get_template_raises_not_found(self):
        # Act / Assert
        with pytest.raises(NotFound):
            template_service.get_template(email_type=EMAIL_TYPE, pk=999999, shop_idx="any")

    def test_update_template_persists_subject(self):
        # Arrange
        template = AccountsNewAccountFactory(subject="Original Subject")

        # Act
        updated = template_service.update_template(
            email_type=EMAIL_TYPE, pk=template.pk, shop_idx=template.channel.idx, subject="Updated Subject"
        )

        # Assert
        assert updated.subject == "Updated Subject"
        template.refresh_from_db()
        assert template.subject == "Updated Subject"

    def test_update_template_clears_field_to_none(self):
        # Arrange
        template = AccountsNewAccountFactory(subject="Has subject")

        # Act
        updated = template_service.update_template(
            email_type=EMAIL_TYPE, pk=template.pk, shop_idx=template.channel.idx, subject=None
        )

        # Assert
        assert updated.subject is None

    def test_update_template_raises_not_found(self):
        # Act / Assert
        with pytest.raises(NotFound):
            template_service.update_template(email_type=EMAIL_TYPE, pk=999999, shop_idx="any", subject="X")

    def test_update_template_partial_leaves_other_fields(self):
        # Arrange
        template = AccountsNewAccountFactory(subject="Subject", welcome="Welcome", announce="Announce")

        # Act
        template_service.update_template(
            email_type=EMAIL_TYPE, pk=template.pk, shop_idx=template.channel.idx, subject="New Subject"
        )

        # Assert
        template.refresh_from_db()
        assert template.subject == "New Subject"
        assert template.welcome == "Welcome"
        assert template.announce == "Announce"


# ---------------------------------------------------------------------------
# template_service — contact_forms slugs (parametrized)
# ---------------------------------------------------------------------------

CONTACT_FORM_SLUGS_AND_FACTORIES = [
    ("contact-forms-booking-confirmation", ContactFormsBookingConfirmationFactory),
    ("contact-forms-booking-admin-notification", ContactFormsBookingAdminNotificationFactory),
    ("contact-forms-submission", ContactFormsSubmissionFactory),
]


@pytest.mark.django_db
class TestTemplateServiceContactForms:
    @pytest.mark.parametrize("slug,factory_class", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_list_routes_to_correct_model(self, slug, factory_class):
        # Arrange
        channel = ChannelFactory()
        instance = factory_class(channel=channel)

        # Act
        result = template_service.list_templates(email_type=slug, shop_idx=channel.idx)

        # Assert
        assert result.count() == 1
        assert result.first().pk == instance.pk

    @pytest.mark.parametrize("slug,factory_class", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_get_returns_instance(self, slug, factory_class):
        # Arrange
        channel = ChannelFactory()
        instance = factory_class(channel=channel)

        # Act
        result = template_service.get_template(email_type=slug, pk=instance.pk, shop_idx=channel.idx)

        # Assert
        assert result.pk == instance.pk

    @pytest.mark.parametrize("slug,factory_class", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_update_persists_header_title(self, slug, factory_class):
        # Arrange
        channel = ChannelFactory()
        instance = factory_class(channel=channel)

        # Act
        template_service.update_template(
            email_type=slug,
            pk=instance.pk,
            shop_idx=channel.idx,
            header_title="Custom heading",
        )

        # Assert
        instance.refresh_from_db()
        assert instance.header_title == "Custom heading"


# ---------------------------------------------------------------------------
# variables_as_dict() — new fields included for all 3 contact_forms models
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestContactFormsVariablesAsDict:
    def test_booking_confirmation_includes_all_new_keys(self):
        channel = ChannelFactory()
        instance = ContactFormsBookingConfirmationFactory(channel=channel)
        result = instance.variables_as_dict()
        for key in (
            "header_title",
            "greeting_template",
            "intro_copy",
            "label_datetime",
            "label_email",
            "label_phone",
            "label_company",
            "label_message",
            "label_video",
            "closing_copy",
        ):
            assert key in result, f"missing key: {key}"
            assert result[key] is not None  # `or ""` guarantees no None

    def test_booking_admin_notification_includes_all_new_keys(self):
        channel = ChannelFactory()
        instance = ContactFormsBookingAdminNotificationFactory(channel=channel)
        result = instance.variables_as_dict()
        for key in (
            "header_title",
            "intro_copy",
            "label_datetime",
            "label_name",
            "label_email",
            "label_phone",
            "label_company",
            "label_message",
            "label_video",
            "closing_copy",
        ):
            assert key in result
            assert result[key] is not None

    def test_contact_form_submission_includes_all_new_keys(self):
        channel = ChannelFactory()
        instance = ContactFormsSubmissionFactory(channel=channel)
        result = instance.variables_as_dict()
        for key in (
            "header_title",
            "intro_copy",
            "label_email",
            "label_type",
            "label_form",
            "label_code",
            "label_body",
            "closing_copy",
        ):
            assert key in result
            assert result[key] is not None


# ---------------------------------------------------------------------------
# Booking confirmation greeting placeholder resolution
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBookingConfirmationGreetingResolver:
    """Service-level test: greeting_template |booker_name| placeholder resolution."""

    def _make_service_with_greeting(self, idx: str, greeting: str):
        from django_email.service.contact_forms.booking_confirmation import BookingConfirmationEmail

        # EmailService requires Language record for active language (default "pl") to exist
        pl = _get_or_create_language("pl")
        channel = ChannelFactory(idx=idx)
        ContactFormsBookingConfirmationFactory(channel=channel, language=pl, greeting_template=greeting)
        return BookingConfirmationEmail(exception_type=Exception, language="pl", channel_idx=idx)

    def test_placeholder_replaced_when_booker_name_present(self):
        svc = self._make_service_with_greeting("resolver-test", "Cześć |booker_name|,")

        ctx = svc.prepare_context({"booker_name": "Anna"})

        assert ctx["greeting_template"] == "Cześć Anna,"

    def test_placeholder_resolved_to_empty_when_booker_name_missing(self):
        svc = self._make_service_with_greeting("resolver-empty", "Cześć |booker_name|,")

        ctx = svc.prepare_context({"booker_name": ""})

        # Placeholder cleared (no literal token leaked to mail)
        assert "|booker_name|" not in ctx["greeting_template"]
        assert ctx["greeting_template"] == "Cześć ,"

    def test_no_placeholder_means_no_op(self):
        svc = self._make_service_with_greeting("resolver-noop", "Witaj!")

        ctx = svc.prepare_context({"booker_name": "Anna"})

        assert ctx["greeting_template"] == "Witaj!"


@pytest.mark.django_db
class TestContactFormSubmissionSubjectFormId:
    """Service-level test: <contact_form_id> in the subject expands to the submission id.

    A constant subject is what makes Gmail collapse every submission into one
    conversation; the id is what keeps them apart. The placeholder is the only
    trigger — an operator who leaves it out keeps the old behaviour.
    """

    def _make_service(self, idx: str, subject: str | None = None):
        from django_email.service.contact_forms.contact_form_submission import ContactFormSubmissionEmail

        # EmailService requires the Language record for the active language to exist.
        language = _get_or_create_language("en")
        channel = ChannelFactory(idx=idx)
        if subject is not None:
            ContactFormsSubmissionFactory(channel=channel, language=language, subject=subject)
        return ContactFormSubmissionEmail(exception_type=Exception, language="en", channel_idx=idx)

    def test_shipped_default_subject_carries_the_id(self):
        # No operator row -> get_subject() default, which ships with the placeholder.
        service = self._make_service("form-id-default")

        ctx = service.prepare_context({"form_id": "482910375562"})

        assert ctx["subject"].endswith(" #482910375562")
        assert "<contact_form_id>" not in ctx["subject"]

    def test_placeholder_picks_the_position(self):
        service = self._make_service("form-id-placeholder", subject="Submission <contact_form_id> from the form")

        ctx = service.prepare_context({"form_id": "482910375562"})

        assert ctx["subject"] == "Submission 482910375562 from the form"

    def test_operator_subject_without_placeholder_is_left_alone(self):
        service = self._make_service("form-id-optout", subject="New submission")

        ctx = service.prepare_context({"form_id": "482910375562"})

        assert ctx["subject"] == "New submission"

    def test_two_submissions_get_distinct_subjects(self):
        service = self._make_service("form-id-distinct")

        first = service.prepare_context({"form_id": "111111111111"})["subject"]
        second = service.prepare_context({"form_id": "222222222222"})["subject"]

        assert first != second

    def test_missing_form_id_drops_the_placeholder(self):
        # An older django-contact-forms sends no form_id; the token must not leak to the mailbox.
        service = self._make_service("form-id-absent", subject="New submission <contact_form_id>")

        ctx = service.prepare_context({})

        assert ctx["subject"] == "New submission"

    def test_sent_message_carries_the_id_in_the_subject(self, settings):
        """End-to-end through send(): the header the mailbox actually sees."""
        from django.core import mail

        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        mail.outbox = []
        service = self._make_service("form-id-outbox", subject="New submission #<contact_form_id>")

        service.send(email=["contact@shop.example"], submission_context={"form_id": "482910375562"})

        assert mail.outbox[0].subject == "New submission #482910375562"
