# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

# Contact-forms models use `default=""` instead of `null=True` (see docs/multilang-emails.md)
# but the API response contract requires absent values to be null. This validator coerces
# empty strings to None on response serialization without changing model storage.
NullableStr = Annotated[str | None, BeforeValidator(lambda v: None if v == "" else v)]


class AccountsNewAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    channel_id: int = Field(description="Channel FK", examples=[1])
    language_id: int | None = Field(None, description="Language FK", examples=[1])
    subject: str | None = Field(None, description="Email subject line", examples=["Welcome to our store!"])
    welcome: str | None = Field(
        None, description="Welcome message (supports |user_name| placeholder)", examples=["Hello |user_name|!"]
    )
    announce: str | None = Field(None, description="Announcement text")
    confirm_button: str | None = Field(None, description="Confirmation button label")
    thank_you: str | None = Field(None, description="Thank you message")
    help: str | None = Field(None, description="Help/support text")


class AccountsResetPasswordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    channel_id: int = Field(description="Channel FK", examples=[1])
    language_id: int | None = Field(None, description="Language FK", examples=[1])
    subject: str | None = Field(None, description="Email subject line")
    welcome: str | None = Field(None, description="Welcome message")
    reset_button: str | None = Field(None, description="Reset button label")
    help: str | None = Field(None, description="Help/support text")


class CheckoutVirtualProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    channel_id: int = Field(description="Channel FK", examples=[1])
    language_id: int | None = Field(None, description="Language FK", examples=[1])
    subject: str | None = Field(None, description="Email subject (supports |order_id|)")
    welcome: str | None = Field(None, description="Welcome message (supports |user_name|)")
    order: str | None = Field(None, description="Order info text (supports |order_id|)")
    products: str | None = Field(None, description="Products section header")
    key_name: str | None = Field(None, description="Product key label")
    additional_key_name: str | None = Field(None, description="Additional key label")
    instructions: str | None = Field(None, description="Instructions section header")
    help: str | None = Field(None, description="Help/support text")


class LoyaltyCouponConfirmationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    channel_id: int = Field(description="Channel FK", examples=[1])
    language_id: int | None = Field(None, description="Language FK", examples=[1])
    subject: str | None = Field(None, description="Email subject line")
    welcome: str | None = Field(None, description="Welcome message (supports |user_name|)")
    thank_you: str | None = Field(None, description="Thank you message")
    coupon_copy: str | None = Field(None, description="Coupon description text")
    coupon_button: str | None = Field(None, description="Coupon button label")
    help: str | None = Field(None, description="Help/support text")


class ReturnsReturnConfirmationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    channel_id: int = Field(description="Channel FK", examples=[1])
    language_id: int | None = Field(None, description="Language FK", examples=[1])
    subject: str | None = Field(None, description="Email subject line")
    welcome: str | None = Field(None, description="Welcome message (supports |user_name|)")
    return_copy: str | None = Field(None, description="Return info (supports |order_id|, |return_id|)")
    comment_copy: str | None = Field(None, description="Comment section text")
    print_copy: str | None = Field(None, description="Print instructions text")
    help: str | None = Field(None, description="Help/support text")


class AllegroVirtualProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    channel_id: int = Field(description="Channel FK", examples=[1])
    language_id: int | None = Field(None, description="Language FK", examples=[1])
    subject: str | None = Field(None, description="Email subject (supports |order_id|)")
    welcome: str | None = Field(None, description="Welcome message (supports |user_name|)")
    order: str | None = Field(None, description="Order info text (supports |order_id|)")
    products: str | None = Field(None, description="Products section header")
    key_name: str | None = Field(None, description="Product key label")
    additional_key_name: str | None = Field(None, description="Additional key label")
    instructions: str | None = Field(None, description="Instructions section header")
    help: str | None = Field(None, description="Help/support text")


class AgreementsNewsletterSignupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    channel_id: int = Field(description="Channel FK", examples=[1])
    language_id: int | None = Field(None, description="Language FK", examples=[1])
    subject: str | None = Field(None, description="Email subject line")
    welcome: str | None = Field(None, description="Welcome message (supports |user_name|)")
    confirm_copy: str | None = Field(None, description="Confirmation description text")
    confirm_button: str | None = Field(None, description="Confirmation button label")
    help: str | None = Field(None, description="Help/support text")


class ContactFormsBookingConfirmationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    channel_id: int = Field(description="Channel FK", examples=[1])
    language_id: int | None = Field(None, description="Language FK", examples=[1])
    subject: NullableStr = Field(
        None, description="Email subject line", examples=["Twoja rezerwacja jest potwierdzona"]
    )
    header_title: NullableStr = Field(
        None, description="H2 heading at the top of the email", examples=["Twoja rezerwacja jest potwierdzona"]
    )
    greeting_template: NullableStr = Field(
        None,
        description="Greeting line. Use |booker_name| placeholder for booker's name",
        examples=["Cześć |booker_name|,"],
    )
    intro_copy: NullableStr = Field(
        None,
        description="Paragraph rendered above the booking facts",
        examples=["Zarezerwowaliśmy Twój termin. Szczegóły poniżej."],
    )
    label_datetime: NullableStr = Field(
        None, description="Table label for the date & time row", examples=["Data i godzina"]
    )
    label_email: NullableStr = Field(None, description="Table label for the email row", examples=["Adres e-mail"])
    label_phone: NullableStr = Field(None, description="Table label for the phone row", examples=["Telefon"])
    label_company: NullableStr = Field(None, description="Table label for the company row", examples=["Firma"])
    label_message: NullableStr = Field(None, description="Table label for the message row", examples=["Wiadomość"])
    label_video: NullableStr = Field(
        None, description="Inline label before the video meeting link", examples=["Rozmowa wideo"]
    )
    closing_copy: NullableStr = Field(
        None,
        description="Paragraph rendered after the meet link",
        examples=["Jeśli termin Ci nie pasuje, odpisz na tego maila."],
    )


class ContactFormsBookingAdminNotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    channel_id: int = Field(description="Channel FK", examples=[1])
    language_id: int | None = Field(None, description="Language FK", examples=[1])
    subject: NullableStr = Field(None, description="Email subject line", examples=["Nowa rezerwacja"])
    header_title: NullableStr = Field(None, description="H2 heading", examples=["Nowa rezerwacja"])
    intro_copy: NullableStr = Field(
        None,
        description="Paragraph rendered above the booking facts",
        examples=["Na Twojej stronie pojawiła się nowa rezerwacja."],
    )
    label_datetime: NullableStr = Field(
        None, description="Table label for the date & time row", examples=["Data i godzina"]
    )
    label_name: NullableStr = Field(None, description="Table label for the name row", examples=["Imię i nazwisko"])
    label_email: NullableStr = Field(None, description="Table label for the email row", examples=["Adres e-mail"])
    label_phone: NullableStr = Field(None, description="Table label for the phone row", examples=["Telefon"])
    label_company: NullableStr = Field(None, description="Table label for the company row", examples=["Firma"])
    label_message: NullableStr = Field(None, description="Table label for the message row", examples=["Wiadomość"])
    label_video: NullableStr = Field(
        None, description="Inline label before the video meeting link", examples=["Rozmowa wideo"]
    )
    closing_copy: NullableStr = Field(None, description="Paragraph rendered after the meet link")


class ContactFormsSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: int = Field(description="Primary key", examples=[1])
    channel_id: int = Field(description="Channel FK", examples=[1])
    language_id: int | None = Field(None, description="Language FK", examples=[1])
    subject: NullableStr = Field(
        None,
        description="Email subject line; <contact_form_id> is substituted with the submission id",
        examples=["New contact form submission #<contact_form_id>"],
    )
    header_title: NullableStr = Field(None, description="H2 heading", examples=["Nowe zgłoszenie z formularza"])
    intro_copy: NullableStr = Field(None, description="Paragraph rendered above the submission facts")
    label_email: NullableStr = Field(None, description="Table label for the email row", examples=["Adres e-mail"])
    label_type: NullableStr = Field(None, description="Table label for the type row", examples=["Typ"])
    label_form: NullableStr = Field(None, description="Table label for the form row", examples=["Formularz"])
    label_code: NullableStr = Field(None, description="Table label for the code row", examples=["Kod"])
    label_body: NullableStr = Field(None, description="Table label for the body row", examples=["Treść"])
    closing_copy: NullableStr = Field(None, description="Paragraph rendered after the body")


class TemplateListResponse(BaseModel):
    count: int = Field(description="Total number of templates", examples=[2], ge=0)
    next: str | None = Field(None, description="Next page URL")
    previous: str | None = Field(None, description="Previous page URL")
    results: list[dict] = Field(description="Template list")
