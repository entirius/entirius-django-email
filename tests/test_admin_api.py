# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Integration tests for the django-email admin API (v2).

Covers all endpoints under /api/email/v2/admin/ including:
- Authentication: 401 / 403 / 200 for every guarded route
- Channels: list, retrieve, partial_update (no DELETE)
- LangChannelConfig: list (nested), retrieve, partial_update (no DELETE)
- Templates: list by type, retrieve, partial_update (no DELETE)
- Pagination: page/page_size params
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import (
    AccountsNewAccountFactory,
    ChannelFactory,
    ContactFormsBookingAdminNotificationFactory,
    ContactFormsBookingConfirmationFactory,
    ContactFormsSubmissionFactory,
    LangChannelConfigFactory,
)

SHOP_IDX = "default-europe"


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------


def channels_list_url(shop_idx: str = SHOP_IDX) -> str:
    return f"/api/email/v2/admin/{shop_idx}/channels/"


def channel_detail_url(pk: int, shop_idx: str = SHOP_IDX) -> str:
    return f"/api/email/v2/admin/{shop_idx}/channels/{pk}/"


def lang_configs_nested_url(channel_pk: int, shop_idx: str = SHOP_IDX) -> str:
    return f"/api/email/v2/admin/{shop_idx}/channels/{channel_pk}/lang-configs/"


def lang_config_detail_url(pk: int, shop_idx: str = SHOP_IDX) -> str:
    return f"/api/email/v2/admin/{shop_idx}/lang-configs/{pk}/"


def templates_list_url(email_type: str, shop_idx: str = SHOP_IDX) -> str:
    return f"/api/email/v2/admin/{shop_idx}/templates/{email_type}/"


def template_detail_url(email_type: str, pk: int, shop_idx: str = SHOP_IDX) -> str:
    return f"/api/email/v2/admin/{shop_idx}/templates/{email_type}/{pk}/"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="admin", email="admin@test.com", password="adminpass123", is_staff=True, is_superuser=False
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username="regular", email="regular@test.com", password="regularpass123", is_staff=False, is_superuser=False
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_user(
        username="super", email="super@test.com", password="superpass123", is_staff=False, is_superuser=True
    )


@pytest.fixture
def admin_token(admin_user):
    return str(RefreshToken.for_user(admin_user).access_token)


@pytest.fixture
def regular_token(regular_user):
    return str(RefreshToken.for_user(regular_user).access_token)


@pytest.fixture
def superuser_token(superuser):
    return str(RefreshToken.for_user(superuser).access_token)


@pytest.fixture
def authenticated_client(api_client, admin_token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
    return api_client


@pytest.fixture
def channel(db):
    return ChannelFactory(idx=SHOP_IDX, label="Default Europe")


@pytest.fixture
def lang_config(channel):
    return LangChannelConfigFactory(channel=channel, language=None)


@pytest.fixture
def lang_config_en(channel):
    return LangChannelConfigFactory(channel=channel, language="en")


@pytest.fixture
def template(channel):
    return AccountsNewAccountFactory(channel=channel, language=None, subject="Test Subject", welcome="Hello!")


# ---------------------------------------------------------------------------
# 1. Authentication
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAuthentication:
    def test_unauthenticated_request_returns_401(self, api_client):
        # Act
        response = api_client.get(channels_list_url())

        # Assert
        assert response.status_code == 401

    def test_regular_user_returns_403(self, api_client, regular_token):
        # Arrange
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {regular_token}")

        # Act
        response = api_client.get(channels_list_url())

        # Assert
        assert response.status_code == 403

    def test_admin_user_returns_200(self, api_client, admin_token, channel):
        # Arrange
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")

        # Act
        response = api_client.get(channels_list_url())

        # Assert
        assert response.status_code == 200

    def test_superuser_returns_200(self, api_client, superuser_token, channel):
        # Arrange
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {superuser_token}")

        # Act
        response = api_client.get(channels_list_url())

        # Assert
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# 2. Channel Endpoints
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestChannelList:
    def test_list_returns_200(self, authenticated_client, channel):
        # Act
        response = authenticated_client.get(channels_list_url())

        # Assert
        assert response.status_code == 200

    def test_list_returns_pagination_fields(self, authenticated_client, channel):
        # Act
        response = authenticated_client.get(channels_list_url())
        data = response.json()

        # Assert
        for field in ("count", "next", "previous", "results"):
            assert field in data

    def test_list_results_contain_channel(self, authenticated_client, channel):
        # Act
        response = authenticated_client.get(channels_list_url())
        data = response.json()

        # Assert
        idxs = [r["idx"] for r in data["results"]]
        assert channel.idx in idxs

    def test_list_page_size_respected(self, authenticated_client, db):
        # Arrange
        ChannelFactory.create_batch(5)

        # Act
        response = authenticated_client.get(channels_list_url() + "?page_size=2")
        data = response.json()

        # Assert
        assert len(data["results"]) <= 2

    def test_delete_not_allowed(self, authenticated_client, channel):
        # Act
        response = authenticated_client.delete(channel_detail_url(pk=channel.pk))

        # Assert
        assert response.status_code == 405


@pytest.mark.django_db
class TestChannelRetrieve:
    def test_retrieve_returns_200(self, authenticated_client, channel):
        # Act
        response = authenticated_client.get(channel_detail_url(pk=channel.pk))

        # Assert
        assert response.status_code == 200

    def test_retrieve_returns_correct_fields(self, authenticated_client, channel):
        # Act
        response = authenticated_client.get(channel_detail_url(pk=channel.pk))
        data = response.json()

        # Assert
        assert data["pk"] == channel.pk
        assert data["idx"] == channel.idx
        assert data["label"] == channel.label
        assert "main_background_color" in data
        assert "font_family" in data

    def test_retrieve_not_found_returns_404(self, authenticated_client, db):
        # Act
        response = authenticated_client.get(channel_detail_url(pk=999999))

        # Assert
        assert response.status_code == 404


@pytest.mark.django_db
class TestChannelUpdate:
    def test_patch_updates_color(self, authenticated_client, channel):
        # Act
        response = authenticated_client.patch(
            channel_detail_url(pk=channel.pk), {"main_background_color": "#AABBCC"}, format="json"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["main_background_color"] == "#AABBCC"
        channel.refresh_from_db()
        assert channel.main_background_color == "#AABBCC"

    def test_patch_updates_sender_info(self, authenticated_client, channel):
        # Act
        response = authenticated_client.patch(
            channel_detail_url(pk=channel.pk), {"from_name": "New Name", "from_email": "new@test.com"}, format="json"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["from_name"] == "New Name"
        assert data["from_email"] == "new@test.com"

    def test_patch_partial_does_not_overwrite_other_fields(self, authenticated_client, channel):
        # Arrange
        original_label = channel.label

        # Act
        authenticated_client.patch(channel_detail_url(pk=channel.pk), {"from_name": "Updated"}, format="json")

        # Assert
        channel.refresh_from_db()
        assert channel.label == original_label

    def test_patch_not_found_returns_404(self, authenticated_client, db):
        # Act
        response = authenticated_client.patch(channel_detail_url(pk=999999), {"from_name": "X"}, format="json")

        # Assert
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# 3. LangChannelConfig Endpoints
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestLangChannelConfigList:
    def test_nested_list_returns_200(self, authenticated_client, channel, lang_config):
        # Act
        response = authenticated_client.get(lang_configs_nested_url(channel_pk=channel.pk))

        # Assert
        assert response.status_code == 200

    def test_nested_list_returns_pagination_fields(self, authenticated_client, channel, lang_config):
        # Act
        response = authenticated_client.get(lang_configs_nested_url(channel_pk=channel.pk))
        data = response.json()

        # Assert
        for field in ("count", "next", "previous", "results"):
            assert field in data

    def test_nested_list_filters_to_channel(self, authenticated_client, channel, lang_config):
        # Arrange
        other_channel = ChannelFactory()
        LangChannelConfigFactory(channel=other_channel)

        # Act
        response = authenticated_client.get(lang_configs_nested_url(channel_pk=channel.pk))
        data = response.json()

        # Assert
        for result in data["results"]:
            assert result["channel_id"] == channel.pk


@pytest.mark.django_db
class TestLangChannelConfigRetrieve:
    def test_retrieve_returns_200(self, authenticated_client, lang_config):
        # Act
        response = authenticated_client.get(lang_config_detail_url(pk=lang_config.pk))

        # Assert
        assert response.status_code == 200

    def test_retrieve_returns_correct_fields(self, authenticated_client, lang_config):
        # Act
        response = authenticated_client.get(lang_config_detail_url(pk=lang_config.pk))
        data = response.json()

        # Assert
        assert data["pk"] == lang_config.pk
        assert data["channel_id"] == lang_config.channel_id
        assert "header_mail" in data
        assert "footer_copy" in data

    def test_retrieve_not_found_returns_404(self, authenticated_client, db):
        # Act
        response = authenticated_client.get(lang_config_detail_url(pk=999999))

        # Assert
        assert response.status_code == 404

    def test_delete_not_allowed(self, authenticated_client, lang_config):
        # Act
        response = authenticated_client.delete(lang_config_detail_url(pk=lang_config.pk))

        # Assert
        assert response.status_code == 405


@pytest.mark.django_db
class TestLangChannelConfigUpdate:
    def test_patch_updates_footer_copy(self, authenticated_client, lang_config):
        # Act
        response = authenticated_client.patch(
            lang_config_detail_url(pk=lang_config.pk), {"footer_copy": "Updated footer"}, format="json"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["footer_copy"] == "Updated footer"

    def test_patch_updates_social_links(self, authenticated_client, lang_config):
        # Act
        response = authenticated_client.patch(
            lang_config_detail_url(pk=lang_config.pk),
            {"footer_link_facebook": "https://facebook.com/test"},
            format="json",
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["footer_link_facebook"] == "https://facebook.com/test"

    def test_patch_not_found_returns_404(self, authenticated_client, db):
        # Act
        response = authenticated_client.patch(lang_config_detail_url(pk=999999), {"footer_copy": "X"}, format="json")

        # Assert
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# 4. Email Template Endpoints
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTemplateList:
    def test_list_returns_200(self, authenticated_client, channel, template):
        # Act
        response = authenticated_client.get(templates_list_url("accounts-new-account", shop_idx=channel.idx))

        # Assert
        assert response.status_code == 200

    def test_list_returns_pagination_fields(self, authenticated_client, channel, template):
        # Act
        response = authenticated_client.get(templates_list_url("accounts-new-account", shop_idx=channel.idx))
        data = response.json()

        # Assert
        for field in ("count", "next", "previous", "results"):
            assert field in data

    def test_list_returns_templates_for_channel(self, authenticated_client, channel, template):
        # Act
        response = authenticated_client.get(templates_list_url("accounts-new-account", shop_idx=channel.idx))
        data = response.json()

        # Assert
        assert data["count"] >= 1

    def test_list_unknown_type_returns_404(self, authenticated_client, db):
        # Act
        response = authenticated_client.get(templates_list_url("unknown-type"))

        # Assert
        assert response.status_code == 404

    def test_list_returns_empty_for_nonexistent_channel(self, authenticated_client, db):
        # Act
        response = authenticated_client.get(templates_list_url("accounts-new-account", shop_idx="no-such-channel"))
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert data["count"] == 0

    def test_delete_not_allowed(self, authenticated_client, channel, template):
        # Act
        response = authenticated_client.delete(
            template_detail_url("accounts-new-account", pk=template.pk, shop_idx=channel.idx)
        )

        # Assert
        assert response.status_code == 405


@pytest.mark.django_db
class TestTemplateRetrieve:
    def test_retrieve_returns_200(self, authenticated_client, channel, template):
        # Act
        response = authenticated_client.get(
            template_detail_url("accounts-new-account", pk=template.pk, shop_idx=channel.idx)
        )

        # Assert
        assert response.status_code == 200

    def test_retrieve_returns_correct_fields(self, authenticated_client, channel, template):
        # Act
        response = authenticated_client.get(
            template_detail_url("accounts-new-account", pk=template.pk, shop_idx=channel.idx)
        )
        data = response.json()

        # Assert
        assert data["pk"] == template.pk
        assert data["channel_id"] == channel.pk
        assert data["subject"] == template.subject
        assert "welcome" in data
        assert "announce" in data

    def test_retrieve_null_fields_returned_as_null(self, authenticated_client, channel, db):
        # Arrange
        t = AccountsNewAccountFactory(channel=channel, subject=None, welcome=None, language=None)

        # Act
        response = authenticated_client.get(template_detail_url("accounts-new-account", pk=t.pk, shop_idx=channel.idx))
        data = response.json()

        # Assert
        assert data["subject"] is None
        assert data["welcome"] is None

    def test_retrieve_not_found_returns_404(self, authenticated_client, channel, db):
        # Act
        response = authenticated_client.get(
            template_detail_url("accounts-new-account", pk=999999, shop_idx=channel.idx)
        )

        # Assert
        assert response.status_code == 404

    def test_retrieve_unknown_type_returns_404(self, authenticated_client, channel, template):
        # Act
        response = authenticated_client.get(template_detail_url("unknown-type", pk=template.pk, shop_idx=channel.idx))

        # Assert
        assert response.status_code == 404


@pytest.mark.django_db
class TestTemplateUpdate:
    def test_patch_updates_subject(self, authenticated_client, channel, template):
        # Act
        response = authenticated_client.patch(
            template_detail_url("accounts-new-account", pk=template.pk, shop_idx=channel.idx),
            {"subject": "New Subject"},
            format="json",
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["subject"] == "New Subject"
        template.refresh_from_db()
        assert template.subject == "New Subject"

    def test_patch_updates_multiple_text_fields(self, authenticated_client, channel, template):
        # Act
        response = authenticated_client.patch(
            template_detail_url("accounts-new-account", pk=template.pk, shop_idx=channel.idx),
            {"subject": "Updated Subject", "welcome": "Updated Welcome", "announce": "Updated Announce"},
            format="json",
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["subject"] == "Updated Subject"
        assert data["welcome"] == "Updated Welcome"
        assert data["announce"] == "Updated Announce"

    def test_patch_clears_field_to_null(self, authenticated_client, channel, template):
        # Act
        response = authenticated_client.patch(
            template_detail_url("accounts-new-account", pk=template.pk, shop_idx=channel.idx),
            {"subject": None},
            format="json",
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["subject"] is None

    def test_patch_not_found_returns_404(self, authenticated_client, channel, db):
        # Act
        response = authenticated_client.patch(
            template_detail_url("accounts-new-account", pk=999999, shop_idx=channel.idx),
            {"subject": "X"},
            format="json",
        )

        # Assert
        assert response.status_code == 404

    def test_patch_unknown_type_returns_404(self, authenticated_client, channel, template):
        # Act
        response = authenticated_client.patch(
            template_detail_url("unknown-type", pk=template.pk, shop_idx=channel.idx), {"subject": "X"}, format="json"
        )

        # Assert
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# 5. Pagination
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPagination:
    def test_channel_list_page_param(self, authenticated_client, db):
        # Arrange
        ChannelFactory.create_batch(5)

        # Act
        response = authenticated_client.get(channels_list_url() + "?page=1&page_size=2")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data["results"]) <= 2

    def test_channel_list_max_page_size_enforced(self, authenticated_client, db):
        # Arrange
        ChannelFactory.create_batch(5)

        # Act
        response = authenticated_client.get(channels_list_url() + "?page_size=200")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data["results"]) <= 100

    def test_template_list_page_size(self, authenticated_client, channel, db):
        # Arrange
        AccountsNewAccountFactory.create_batch(5, channel=channel)

        # Act
        response = authenticated_client.get(
            templates_list_url("accounts-new-account", shop_idx=channel.idx) + "?page_size=2"
        )
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data["results"]) <= 2


# ---------------------------------------------------------------------------
# 9. Contact-forms email types (parametrized over 3 new slugs)
# ---------------------------------------------------------------------------


CONTACT_FORM_SLUGS_AND_FACTORIES = [
    ("contact-forms-booking-confirmation", ContactFormsBookingConfirmationFactory),
    ("contact-forms-booking-admin-notification", ContactFormsBookingAdminNotificationFactory),
    ("contact-forms-submission", ContactFormsSubmissionFactory),
]


@pytest.mark.django_db
class TestContactFormsTemplatesAuth:
    @pytest.mark.parametrize("email_type,_factory", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_unauthenticated_returns_401(self, api_client, channel, email_type, _factory):
        response = api_client.get(templates_list_url(email_type, shop_idx=channel.idx))
        assert response.status_code == 401

    @pytest.mark.parametrize("email_type,_factory", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_regular_user_returns_403(self, api_client, regular_token, channel, email_type, _factory):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {regular_token}")
        response = api_client.get(templates_list_url(email_type, shop_idx=channel.idx))
        assert response.status_code == 403

    @pytest.mark.parametrize("email_type,_factory", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_admin_returns_200(self, authenticated_client, channel, email_type, _factory):
        response = authenticated_client.get(templates_list_url(email_type, shop_idx=channel.idx))
        assert response.status_code == 200


@pytest.mark.django_db
class TestContactFormsTemplatesList:
    @pytest.mark.parametrize("email_type,factory_class", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_list_includes_factory_record(self, authenticated_client, channel, email_type, factory_class):
        factory_class(channel=channel)

        response = authenticated_client.get(templates_list_url(email_type, shop_idx=channel.idx))

        assert response.status_code == 200
        assert response.json()["count"] == 1


@pytest.mark.django_db
class TestContactFormsTemplatesRetrieve:
    @pytest.mark.parametrize("email_type,factory_class", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_retrieve_returns_overrides(self, authenticated_client, channel, email_type, factory_class):
        instance = factory_class(channel=channel, header_title="Custom heading")

        response = authenticated_client.get(template_detail_url(email_type, pk=instance.pk, shop_idx=channel.idx))

        assert response.status_code == 200
        data = response.json()
        assert data["pk"] == instance.pk
        assert data["header_title"] == "Custom heading"

    @pytest.mark.parametrize("email_type,factory_class", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_empty_string_serialized_as_null(self, authenticated_client, channel, email_type, factory_class):
        # Model fields default to "" but API contract requires null on response
        instance = factory_class(channel=channel, header_title="")

        response = authenticated_client.get(template_detail_url(email_type, pk=instance.pk, shop_idx=channel.idx))

        assert response.status_code == 200
        assert response.json()["header_title"] is None

    @pytest.mark.parametrize("email_type,_factory", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_retrieve_not_found_returns_404(self, authenticated_client, channel, email_type, _factory):
        response = authenticated_client.get(template_detail_url(email_type, pk=99999, shop_idx=channel.idx))
        assert response.status_code == 404


@pytest.mark.django_db
class TestContactFormsTemplatesUpdate:
    @pytest.mark.parametrize("email_type,factory_class", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_patch_updates_header_title(self, authenticated_client, channel, email_type, factory_class):
        instance = factory_class(channel=channel)

        response = authenticated_client.patch(
            template_detail_url(email_type, pk=instance.pk, shop_idx=channel.idx),
            {"header_title": "Nowy tytuł"},
            format="json",
        )

        assert response.status_code == 200
        assert response.json()["header_title"] == "Nowy tytuł"

    @pytest.mark.parametrize("email_type,factory_class", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_patch_oversized_field_returns_400(self, authenticated_client, channel, email_type, factory_class):
        # header_title cap is 4096 chars; submit 5000
        instance = factory_class(channel=channel)

        response = authenticated_client.patch(
            template_detail_url(email_type, pk=instance.pk, shop_idx=channel.idx),
            {"header_title": "x" * 5000},
            format="json",
        )

        assert response.status_code == 400

    @pytest.mark.parametrize("email_type,_factory", CONTACT_FORM_SLUGS_AND_FACTORIES)
    def test_patch_not_found_returns_404(self, authenticated_client, channel, email_type, _factory):
        response = authenticated_client.patch(
            template_detail_url(email_type, pk=99999, shop_idx=channel.idx),
            {"header_title": "X"},
            format="json",
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# 10. LangChannelConfig footer override fields
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestLangChannelConfigFooterOverrides:
    def test_retrieve_includes_new_footer_fields(self, authenticated_client, lang_config):
        response = authenticated_client.get(lang_config_detail_url(pk=lang_config.pk))

        assert response.status_code == 200
        data = response.json()
        for field in (
            "footer_signature_copy_1",
            "footer_signature_copy_2",
            "footer_socials_copy",
            "footer_automatic_copy",
            "footer_unsubscribe_label",
        ):
            assert field in data
            assert data[field] is None  # default "" coerced to null on response

    def test_patch_updates_signature_copy(self, authenticated_client, lang_config):
        response = authenticated_client.patch(
            lang_config_detail_url(pk=lang_config.pk),
            {"footer_signature_copy_1": "Pozdrawiamy,", "footer_signature_copy_2": "Example Team"},
            format="json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["footer_signature_copy_1"] == "Pozdrawiamy,"
        assert data["footer_signature_copy_2"] == "Example Team"

    def test_patch_oversized_signature_returns_400(self, authenticated_client, lang_config):
        # signature_copy_1 cap is 512 chars
        response = authenticated_client.patch(
            lang_config_detail_url(pk=lang_config.pk),
            {"footer_signature_copy_1": "x" * 1000},
            format="json",
        )
        assert response.status_code == 400

    def test_empty_wysiwyg_normalized_to_null_on_response(self, authenticated_client, lang_config):
        # CMS BasicWysiwyg sends <p></p> for empty content; should be coerced to null
        response = authenticated_client.patch(
            lang_config_detail_url(pk=lang_config.pk),
            {"footer_automatic_copy": "<p></p>"},
            format="json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["footer_automatic_copy"] is None

    def test_wysiwyg_variants_all_normalize_to_null(self, authenticated_client, lang_config):
        # All BasicWysiwyg empty representations should be treated as no content
        for empty_html in ("<p></p>", "<p><br></p>", "<p>&nbsp;</p>", "   ", "<p>\n</p>"):
            response = authenticated_client.patch(
                lang_config_detail_url(pk=lang_config.pk),
                {"footer_copy": empty_html},
                format="json",
            )
            assert response.status_code == 200, f"failed on {empty_html!r}"
            assert response.json()["footer_copy"] is None, f"not normalized: {empty_html!r}"

    def test_wysiwyg_real_content_passes_through(self, authenticated_client, lang_config):
        response = authenticated_client.patch(
            lang_config_detail_url(pk=lang_config.pk),
            {"footer_copy": "<p>Real text</p>"},
            format="json",
        )

        assert response.status_code == 200
        assert response.json()["footer_copy"] == "<p>Real text</p>"
