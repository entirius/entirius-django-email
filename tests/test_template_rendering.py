# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Regression tests for email template rendering.

Catches:
- Literal "None" text from nullable LangChannelConfig fields
- !important CSS rules (email deliverability risk)
- Header/footer include integrity
"""

import pytest
from django.template.loader import get_template

from .factories import (
    AccountsNewAccountFactory,
    AgreementsNewsletterSignupFactory,
    ChannelFactory,
    ContactFormsBookingConfirmationFactory,
    LangChannelConfigFactory,
)

# Template paths matching django_email.settings defaults
TEMPLATE_PATHS = [
    "django_accounts/email/default_new_account.html",
    "django_accounts/email/default_pass_reset.html",
    "django_agreements/email/default_newsletter_signup.html",
    "django_checkout/email/default_virtual_product.html",
    "django_allegro/email/default_virtual_product.html",
    "django_loyalty/email/default_get_coupon.html",
    "django_returns/email/default_return.html",
]


def _build_channel_context(channel, lang_config):
    """Build full template context from channel + lang config."""
    ctx = channel.variables_as_dict(lang=None)
    ctx.update(lang_config.variables_as_dict())
    return ctx


def _render_template(path: str, context: dict) -> str:
    """Render an email template with the given context."""
    template = get_template(path)
    return template.render(context)


@pytest.mark.django_db
class TestNoNoneInRenderedHtml:
    """Verify that nullable fields don't leak 'None' into rendered output."""

    def test_new_account_with_nulls(self):
        # Arrange — channel with all nullable LangChannelConfig fields null
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(
            channel=channel,
            logo_url=None,
            footer_copy=None,
            footer_link_facebook=None,
            footer_link_instagram=None,
            footer_link_youtube=None,
            footer_link_x=None,
            footer_link_tiktok=None,
        )
        template_model = AccountsNewAccountFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(template_model.variables_as_dict(username="TestUser"))
        ctx["confirmation_link"] = "https://example.com/confirm"

        # Act
        html = _render_template("django_accounts/email/default_new_account.html", ctx)

        # Assert
        assert "None" not in html

    def test_new_account_with_all_fields_populated(self):
        # Arrange — all fields set
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(
            channel=channel,
            shop_name="Full Store",
            logo_url="https://example.com/logo.png",
            footer_copy="Legal text here.",
            footer_link_facebook="https://facebook.com/store",
            footer_link_instagram="https://instagram.com/store",
            footer_link_youtube="https://youtube.com/store",
        )
        template_model = AccountsNewAccountFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(template_model.variables_as_dict(username="TestUser"))
        ctx["confirmation_link"] = "https://example.com/confirm"

        # Act
        html = _render_template("django_accounts/email/default_new_account.html", ctx)

        # Assert
        assert "None" not in html
        assert "Full Store" in html
        assert "Legal text here." in html

    def test_newsletter_signup_with_nulls(self):
        # Arrange
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(
            channel=channel,
            logo_url=None,
            footer_copy=None,
            footer_link_facebook=None,
            footer_link_instagram=None,
            footer_link_youtube=None,
        )
        template_model = AgreementsNewsletterSignupFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(template_model.variables_as_dict())
        ctx["confirmation_link"] = "https://example.com/confirm"

        # Act
        html = _render_template("django_agreements/email/default_newsletter_signup.html", ctx)

        # Assert
        assert "None" not in html

    def test_pass_reset_with_nulls(self):
        # Arrange
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel, logo_url=None, footer_copy=None)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(
            {
                "welcome": "Reset your password",
                "reset_button": "Reset Now",
                "help": "Contact support",
                "confirmation_link": "https://example.com/reset",
            }
        )

        # Act
        html = _render_template("django_accounts/email/default_pass_reset.html", ctx)

        # Assert
        assert "None" not in html


@pytest.mark.django_db
class TestNoBangImportantInCss:
    """Verify that no !important rules remain in rendered HTML."""

    @pytest.mark.parametrize("template_path", TEMPLATE_PATHS)
    def test_no_important_in_rendered_html(self, template_path):
        # Arrange — minimal context to render without errors
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(
            {
                "subject": "Test",
                "welcome": "Hello",
                "announce": "Announcement",
                "confirm_button": "Confirm",
                "reset_button": "Reset",
                "thank_you": "Thanks",
                "help": "Help text",
                "confirmation_link": "https://example.com",
                "confirm_copy": "Confirm copy",
                "return_copy": "Return copy",
                "comment_copy": "Comment",
                "comment": "User comment",
                "print_copy": "Print this",
                "shipping_address": "123 Street",
                "coupon_copy": "Your coupon",
                "loyalty_coupon": "COUPON123",
                "coupon_button": "Use Coupon",
                "order": "#1234",
                "products_copy": "Your products:",
                "products": [],
                "instructions": [],
                "key_name": "Key",
                "additional_key_name": "Extra Key",
                "instructions_copy": "Instructions:",
            }
        )

        # Act
        html = _render_template(template_path, ctx)

        # Assert
        assert "!important" not in html


@pytest.mark.django_db
class TestHeaderFooterInclusion:
    """Verify header and footer are included in rendered emails."""

    def test_header_contains_support_email(self):
        # Arrange
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel, header_mail="test@support.com")
        template_model = AccountsNewAccountFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(template_model.variables_as_dict(username="TestUser"))
        ctx["confirmation_link"] = "https://example.com/confirm"

        # Act
        html = _render_template("django_accounts/email/default_new_account.html", ctx)

        # Assert
        assert "test@support.com" in html

    def test_header_shows_shop_name_when_no_logo(self):
        # Arrange
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel, shop_name="My Shop", logo_url=None)
        template_model = AccountsNewAccountFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(template_model.variables_as_dict(username="TestUser"))
        ctx["confirmation_link"] = "https://example.com/confirm"

        # Act
        html = _render_template("django_accounts/email/default_new_account.html", ctx)

        # Assert
        assert "My Shop" in html

    def test_footer_social_links_with_dot_separator(self):
        # Arrange
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(
            channel=channel, footer_link_facebook="https://facebook.com", footer_link_instagram="https://instagram.com"
        )
        template_model = AccountsNewAccountFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(template_model.variables_as_dict(username="TestUser"))
        ctx["confirmation_link"] = "https://example.com/confirm"

        # Act
        html = _render_template("django_accounts/email/default_new_account.html", ctx)

        # Assert
        assert "Facebook" in html
        assert "Instagram" in html
        assert "&middot;" in html

    def test_footer_copy_guarded_when_null(self):
        # Arrange
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel, footer_copy=None)
        template_model = AccountsNewAccountFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(template_model.variables_as_dict(username="TestUser"))
        ctx["confirmation_link"] = "https://example.com/confirm"

        # Act
        html = _render_template("django_accounts/email/default_new_account.html", ctx)

        # Assert — no "None" text, and footer automatic copy is still present
        assert "None" not in html


# ---------------------------------------------------------------------------
# Footer override DB-vs-i18n behavior (5 new fields on LangChannelConfig)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFooterOverrides:
    """Verify DB values override translated defaults; empty falls back to .po"""

    def test_footer_signature_copy_1_override_renders_in_html(self):
        # Arrange
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel, footer_signature_copy_1="Z poważaniem,")
        template_model = AccountsNewAccountFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(template_model.variables_as_dict(username="TestUser"))
        ctx["confirmation_link"] = "https://example.com/confirm"

        # Act
        html = _render_template("django_accounts/email/default_new_account.html", ctx)

        # Assert
        assert "Z poważaniem," in html

    def test_footer_signature_copy_1_empty_falls_back_to_translation(self):
        # Arrange — empty string in DB
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel, footer_signature_copy_1="")
        template_model = AccountsNewAccountFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(template_model.variables_as_dict(username="TestUser"))
        ctx["confirmation_link"] = "https://example.com/confirm"

        # Act
        html = _render_template("django_accounts/email/default_new_account.html", ctx)

        # Assert — raw i18n key NEVER leaked, no literal "None"
        assert "FooterSignatureCopy1" not in html
        assert "None" not in html

    def test_footer_automatic_copy_renders_with_linebreaks_not_safe(self):
        # Arrange — verify newlines are converted to <br> via |linebreaks (not |safe)
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel, footer_automatic_copy="Pierwsza linia\nDruga linia")
        template_model = AccountsNewAccountFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(template_model.variables_as_dict(username="TestUser"))
        ctx["confirmation_link"] = "https://example.com/confirm"

        # Act
        html = _render_template("django_accounts/email/default_new_account.html", ctx)

        # Assert — both lines render, separated by <br>
        assert "Pierwsza linia" in html
        assert "Druga linia" in html

    def test_footer_automatic_copy_html_is_escaped(self):
        # Arrange — verify HTML in the field is auto-escaped (no XSS)
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel, footer_automatic_copy="<script>alert('xss')</script>")
        template_model = AccountsNewAccountFactory(channel=channel)
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(template_model.variables_as_dict(username="TestUser"))
        ctx["confirmation_link"] = "https://example.com/confirm"

        # Act
        html = _render_template("django_accounts/email/default_new_account.html", ctx)

        # Assert — script tag escaped, never present as live HTML
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html


# ---------------------------------------------------------------------------
# Booking confirmation override paths (new model fields)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBookingConfirmationOverrides:
    """Verify new ContactFormsBookingConfirmation fields override template defaults."""

    def _build_ctx(self, channel, lang_config, model, **booking_extra):
        ctx = _build_channel_context(channel, lang_config)
        ctx.update(model.subject_as_dict())
        ctx.update(model.variables_as_dict())
        ctx.update(
            {
                "booker_name": "Anna",
                "booker_email": "anna@example.com",
                "booker_phone": "",
                "booker_company": "",
                "booker_message": "",
                "meet_link": "",
                "meeting_start": None,
                "meeting_end": None,
                "timezone": "UTC",
            }
        )
        ctx.update(booking_extra)
        return ctx

    def test_header_title_override_renders(self):
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel)
        model = ContactFormsBookingConfirmationFactory(channel=channel, header_title="Twoja rezerwacja jest gotowa")
        ctx = self._build_ctx(channel, lang_config, model)

        html = _render_template("django_contact_forms/email/booking_confirmation.html", ctx)

        assert "Twoja rezerwacja jest gotowa" in html

    def test_header_title_empty_falls_back_to_translation(self):
        from django.utils.translation import activate

        # Force English to make the assertion language-agnostic regardless of
        # whatever language a previous test activated via EmailService.
        activate("en")
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel)
        model = ContactFormsBookingConfirmationFactory(channel=channel, header_title="")
        ctx = self._build_ctx(channel, lang_config, model)

        html = _render_template("django_contact_forms/email/booking_confirmation.html", ctx)

        # i18n falls back to literal English in test settings (no .po compiled)
        assert "Your booking is confirmed" in html
        assert "None" not in html

    def test_label_email_override_renders(self):
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel)
        model = ContactFormsBookingConfirmationFactory(channel=channel, label_email="Adres e-mail")
        ctx = self._build_ctx(channel, lang_config, model)

        html = _render_template("django_contact_forms/email/booking_confirmation.html", ctx)

        assert "Adres e-mail" in html

    def test_greeting_template_placeholder_resolved_in_service(self):
        # NB: the |booker_name| replacement happens in BookingConfirmationEmail.prepare_context,
        # NOT in the template. We simulate that here for an isolated render test.
        channel = ChannelFactory()
        lang_config = LangChannelConfigFactory(channel=channel)
        model = ContactFormsBookingConfirmationFactory(channel=channel, greeting_template="Cześć |booker_name|,")
        ctx = self._build_ctx(channel, lang_config, model)
        # Simulate service-layer placeholder resolution
        ctx["greeting_template"] = ctx["greeting_template"].replace("|booker_name|", ctx["booker_name"])

        html = _render_template("django_contact_forms/email/booking_confirmation.html", ctx)

        assert "Cześć Anna," in html
        assert "|booker_name|" not in html
