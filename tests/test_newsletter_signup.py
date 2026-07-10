# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for newsletter signup model and template logic.

Focuses on model behavior:
- AgreementsNewsletterSignup variables_as_dict and subject_as_dict
- Fallback to i18n strings when fields are null
- Placeholder substitution for |user_name|
"""

import pytest

from django_email.models.agreements.newsletter_signup import AgreementsNewsletterSignup

from .factories import AgreementsNewsletterSignupFactory, ChannelFactory

# ---------------------------------------------------------------------------
# AgreementsNewsletterSignup model behavior
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAgreementsNewsletterSignupModel:
    def test_subject_as_dict_returns_subject_when_set(self):
        # Arrange
        template = AgreementsNewsletterSignupFactory(subject="Subscribe Now")

        # Act
        result = template.subject_as_dict()

        # Assert
        assert result == {"subject": "Subscribe Now"}

    def test_subject_as_dict_returns_empty_when_null(self):
        # Arrange
        template = AgreementsNewsletterSignupFactory(subject=None)

        # Act
        result = template.subject_as_dict()

        # Assert
        assert result == {}

    def test_variables_as_dict_returns_custom_fields_when_set(self):
        # Arrange
        template = AgreementsNewsletterSignupFactory(
            welcome="Welcome custom", confirm_copy="Please confirm", confirm_button="Click here", help="Call us"
        )

        # Act
        result = template.variables_as_dict()

        # Assert
        assert result["welcome"] == "Welcome custom"
        assert result["confirm_copy"] == "Please confirm"
        assert result["confirm_button"] == "Click here"
        assert result["help"] == "Call us"

    def test_variables_as_dict_substitutes_user_name_placeholder(self):
        # Arrange
        template = AgreementsNewsletterSignupFactory(welcome="Hello |user_name|!")

        # Act
        result = template.variables_as_dict(username="Alice")

        # Assert
        assert result["welcome"] == "Hello Alice!"

    def test_variables_as_dict_returns_welcome_without_placeholder_when_no_username(self):
        # Arrange
        template = AgreementsNewsletterSignupFactory(welcome="Hello |user_name|, thanks!")

        # Act
        result = template.variables_as_dict(username=None)

        # Assert
        # When username is None, welcome with placeholder is returned as-is
        assert result["welcome"] == "Hello |user_name|, thanks!"

    def test_variables_as_dict_falls_back_to_i18n_when_fields_null(self):
        # Arrange
        template = AgreementsNewsletterSignupFactory(welcome=None, confirm_copy=None, confirm_button=None, help=None)

        # Act
        result = template.variables_as_dict()

        # Assert
        # Should return non-empty strings from i18n (not None)
        assert result["welcome"] is not None
        assert result["confirm_copy"] is not None
        assert result["confirm_button"] is not None
        assert result["help"] is not None

    def test_str_returns_channel_and_language(self):
        # Arrange
        channel = ChannelFactory(idx="test-ch")
        template = AgreementsNewsletterSignupFactory(channel=channel, language=None)

        # Act
        result = str(template)

        # Assert
        assert "test-ch" in result
        assert "default" in result


@pytest.mark.django_db
class TestAgreementsNewsletterSignupCreation:
    def test_create_with_channel_and_null_language(self):
        # Arrange
        channel = ChannelFactory()

        # Act
        template = AgreementsNewsletterSignup.objects.create(channel=channel, language=None, subject="Test Subject")

        # Assert
        assert template.pk is not None
        assert template.channel == channel
        assert template.language is None
        assert template.subject == "Test Subject"

    def test_all_text_fields_nullable(self):
        # Arrange
        channel = ChannelFactory()

        # Act
        template = AgreementsNewsletterSignup.objects.create(
            channel=channel,
            language=None,
            subject=None,
            welcome=None,
            confirm_copy=None,
            confirm_button=None,
            help=None,
        )

        # Assert
        assert template.subject is None
        assert template.welcome is None
        assert template.confirm_copy is None
        assert template.confirm_button is None
        assert template.help is None
