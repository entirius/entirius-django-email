# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import factory

from django_email.models import (
    AccountsNewAccount,
    AgreementsNewsletterSignup,
    Channel,
    ContactFormsBookingAdminNotification,
    ContactFormsBookingConfirmation,
    ContactFormsSubmission,
    LangChannelConfig,
)


class ChannelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Channel

    idx = factory.Sequence(lambda n: f"channel-{n}")
    label = factory.Sequence(lambda n: f"Channel {n}")
    from_name = "Test Store"
    from_email = "noreply@test.entirius.com"
    main_background_color = "#FFFFFF"
    body_background_color = "#EDEDED"
    main_text_color = "#141414"
    brand_text_color = "#404040"
    font_family = "'Inter', sans-serif"
    logo_max_width = "100"


class LangChannelConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LangChannelConfig

    channel = factory.SubFactory(ChannelFactory)
    language = None
    shop_name = factory.Sequence(lambda n: f"Store {n}")
    header_mail = "support@test.entirius.com"
    footer_name_brand = "Test Brand"
    footer_link_brand = "https://test.entirius.com"


class AccountsNewAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccountsNewAccount

    channel = factory.SubFactory(ChannelFactory)
    language = None
    subject = factory.Sequence(lambda n: f"Welcome Subject {n}")
    welcome = factory.Sequence(lambda n: f"Welcome message {n}")
    announce = "Your account has been created"
    confirm_button = "Confirm Account"
    thank_you = "Thank you"
    help = "Contact support"


class AgreementsNewsletterSignupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AgreementsNewsletterSignup

    channel = factory.SubFactory(ChannelFactory)
    language = None
    subject = factory.Sequence(lambda n: f"Newsletter Subject {n}")
    welcome = factory.Sequence(lambda n: f"Newsletter welcome {n}")
    confirm_copy = "Please confirm your subscription"
    confirm_button = "Confirm"
    help = "Contact support if needed"


class ContactFormsBookingConfirmationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactFormsBookingConfirmation

    channel = factory.SubFactory(ChannelFactory)
    language = None
    subject = factory.Sequence(lambda n: f"Booking confirmed {n}")
    header_title = "Twoja rezerwacja jest potwierdzona"
    intro_copy = "Zarezerwowaliśmy Twój termin."
    label_datetime = "Data i godzina"
    label_email = "Adres e-mail"


class ContactFormsBookingAdminNotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactFormsBookingAdminNotification

    channel = factory.SubFactory(ChannelFactory)
    language = None
    subject = factory.Sequence(lambda n: f"New booking {n}")
    header_title = "Nowa rezerwacja"
    intro_copy = "Pojawiła się nowa rezerwacja."


class ContactFormsSubmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactFormsSubmission

    channel = factory.SubFactory(ChannelFactory)
    language = None
    subject = factory.Sequence(lambda n: f"Form submission {n}")
    header_title = "Nowe zgłoszenie"


def _get_or_create_language(iso2: str):
    from django_regional.models import Language

    lang, _ = Language.objects.get_or_create(
        iso2=iso2,
        defaults={"iso3": iso2 + "u", "name_en": iso2.upper(), "name_pl": iso2.upper(), "name_source": iso2.upper()},
    )
    return lang
