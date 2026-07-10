# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.core.management.base import BaseCommand

from django_email.service.accounts.new_account import NewAccountEmail
from django_email.service.accounts.reset_password import ResetPasswordEmail
from django_email.service.agreements.newsletter_signup import NewsletterSignupEmail
from django_email.service.allegro.virtual_product import VirtualProductEmail as AllegroVirtualProductEmail
from django_email.service.checkout.virtual_product import VirtualProductEmail
from django_email.service.loyalty.coupon_confirmation import CouponConfirmationEmail
from django_email.service.returns.return_confirmation import ReturnConfirmationEmail


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("channel_idx", type=str, help="channel")
        parser.add_argument("to", type=str, help="email address to send the test email")
        parser.add_argument(
            "type",
            type=str,
            help="new_account, reset_password, coupon_confirmation, return_confirmation, virtual_product, allegro_virtual_product, newsletter_signup",
        )
        parser.add_argument("--lang", type=str, help="email language in iso2", default="pl")

    def handle(self, *args, **options):
        channel_idx = options["channel_idx"]
        to = options["to"]
        email_type = options["type"]
        lang = options["lang"]

        match email_type:
            case "new_account":
                test = NewAccountEmail(language=lang, channel_idx=channel_idx)
                test.send(email=[to], username="test", confirmation_link="https://example.com")
            case "reset_password":
                test = ResetPasswordEmail(language=lang, channel_idx=channel_idx)
                test.send(email=[to], confirmation_link="https://example.com")
            case "coupon_confirmation":
                test = CouponConfirmationEmail(language=lang, channel_idx=channel_idx)
                test.send(
                    email=[to], username="test", confirmation_link="https://example.com", loyalty_coupon="TEST123"
                )
            case "return_confirmation":
                test = ReturnConfirmationEmail(language=lang, channel_idx=channel_idx)
                test.send(
                    email=[to],
                    first_name="Test",
                    last_name="Testowy",
                    customer_name="test",
                    customer_username="test",
                    customer_email="test@example.com",
                    return_id="123456789",
                    order_id="ABC123",
                    order_pretty_id="100000000000",
                    shop_shipping_address="Testowa 123 12-123 Testowo",
                    comment="TEST",
                )
            case "virtual_product":
                test = VirtualProductEmail(language=lang, channel_idx=channel_idx)
                products = [
                    VirtualProductEmail.Product(name="Call of Duty", key="1234-5678-9012"),
                    VirtualProductEmail.Product(name="Battlefield", key="9876-5432-1098", additional_key="12345/6789"),
                ]
                instructions = [
                    VirtualProductEmail.Instruction(
                        name="Blizzard Battle.net Digital Code 20 EUR",
                        content="INSTRUKCJA UŻYCIA<br />1. Wejdź na blizzard.com/code.<br />2. Zaloguj się lub stwórz BEZPŁATNE konto Blizzard.<br />3. Wprowadź kod.<br />4. Saldo twojego konta Blizzard jest teraz doładowane środkami, które możesz przeznaczyć na wybrane tytuły Blizzarda.",
                    ),
                    VirtualProductEmail.Instruction(
                        name="Klucz steam",
                        content="Instrukcja rejestracji klucza i aktywacji produktu w serwisie Steam:<br /><br />Zarejestruj i zainstaluj aplikację Steam, którą można pobrać pod adresem http://store.steampowered.com/ (górny prawy róg strony).<br /><br />Wykonaj poniższe czynności, by aktywować nowo zakupiony produkt w Steam:<br /><br />1. Uruchom Steam i zaloguj się na swoje konto Steam.<br /><br />2. Kliknij na menu Gry w górnym pasku (Games).<br /><br />3. Wybierz opcję aktywacji produktu w Steam (Activate a Product on Steam).<br /><br />4. Postępuj zgodnie z instrukcjami na ekranie, by zakończyć proces aktywacji.<br /><br /><br />W artykule dotyczącym kluczy CD znajduje się lista gier, które można aktywować w Steam.",
                    ),
                ]
                test.send(
                    email=[to], username="test", order_id="100000000000", products=products, instructions=instructions
                )
            case "allegro_virtual_product":
                test = AllegroVirtualProductEmail(language=lang, channel_idx=channel_idx)
                products = [
                    VirtualProductEmail.Product(name="Call of Duty", key="1234-5678-9012"),
                    VirtualProductEmail.Product(name="Battlefield", key="9876-5432-1098", additional_key="12345/6789"),
                ]
                instructions = [
                    VirtualProductEmail.Instruction(
                        name="Blizzard Battle.net Digital Code 20 EUR",
                        content="INSTRUKCJA UŻYCIA<br />1. Wejdź na blizzard.com/code.<br />2. Zaloguj się lub stwórz BEZPŁATNE konto Blizzard.<br />3. Wprowadź kod.<br />4. Saldo twojego konta Blizzard jest teraz doładowane środkami, które możesz przeznaczyć na wybrane tytuły Blizzarda.",
                    ),
                    VirtualProductEmail.Instruction(
                        name="Klucz steam",
                        content="Instrukcja rejestracji klucza i aktywacji produktu w serwisie Steam:<br /><br />Zarejestruj i zainstaluj aplikację Steam, którą można pobrać pod adresem http://store.steampowered.com/ (górny prawy róg strony).<br /><br />Wykonaj poniższe czynności, by aktywować nowo zakupiony produkt w Steam:<br /><br />1. Uruchom Steam i zaloguj się na swoje konto Steam.<br /><br />2. Kliknij na menu Gry w górnym pasku (Games).<br /><br />3. Wybierz opcję aktywacji produktu w Steam (Activate a Product on Steam).<br /><br />4. Postępuj zgodnie z instrukcjami na ekranie, by zakończyć proces aktywacji.<br /><br /><br />W artykule dotyczącym kluczy CD znajduje się lista gier, które można aktywować w Steam.",
                    ),
                ]
                test.send(
                    email=[to], username="test", order_id="100000000000", products=products, instructions=instructions
                )
            case "newsletter_signup":
                test = NewsletterSignupEmail(language=lang, channel_idx=channel_idx)
                test.send(email=[to], confirmation_link="https://example.com", username="test")
            case _:
                self.stdout.write(self.style.ERROR("Invalid email type"))
                return

        self.stdout.write(self.style.SUCCESS("DONE"))
