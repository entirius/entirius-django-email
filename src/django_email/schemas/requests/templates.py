# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pydantic import BaseModel, Field

from django_email.schemas.validators import WysiwygStr


class AccountsNewAccountUpdateRequest(BaseModel):
    subject: str | None = Field(None, description="Email subject line")
    welcome: str | None = Field(None, description="Welcome message")
    announce: str | None = Field(None, description="Announcement text")
    confirm_button: str | None = Field(None, description="Confirmation button label")
    thank_you: str | None = Field(None, description="Thank you message")
    help: str | None = Field(None, description="Help/support text")


class AccountsResetPasswordUpdateRequest(BaseModel):
    subject: str | None = Field(None, description="Email subject line")
    welcome: str | None = Field(None, description="Welcome message")
    reset_button: str | None = Field(None, description="Reset button label")
    help: str | None = Field(None, description="Help/support text")


class CheckoutVirtualProductUpdateRequest(BaseModel):
    subject: str | None = Field(None, description="Email subject")
    welcome: str | None = Field(None, description="Welcome message")
    order: str | None = Field(None, description="Order info text")
    products: str | None = Field(None, description="Products section header")
    key_name: str | None = Field(None, description="Product key label")
    additional_key_name: str | None = Field(None, description="Additional key label")
    instructions: str | None = Field(None, description="Instructions section header")
    help: str | None = Field(None, description="Help/support text")


class LoyaltyCouponConfirmationUpdateRequest(BaseModel):
    subject: str | None = Field(None, description="Email subject line")
    welcome: str | None = Field(None, description="Welcome message")
    thank_you: str | None = Field(None, description="Thank you message")
    coupon_copy: str | None = Field(None, description="Coupon description text")
    coupon_button: str | None = Field(None, description="Coupon button label")
    help: str | None = Field(None, description="Help/support text")


class ReturnsReturnConfirmationUpdateRequest(BaseModel):
    subject: str | None = Field(None, description="Email subject line")
    welcome: str | None = Field(None, description="Welcome message")
    return_copy: str | None = Field(None, description="Return info text")
    comment_copy: str | None = Field(None, description="Comment section text")
    print_copy: str | None = Field(None, description="Print instructions text")
    help: str | None = Field(None, description="Help/support text")


class AllegroVirtualProductUpdateRequest(BaseModel):
    subject: str | None = Field(None, description="Email subject")
    welcome: str | None = Field(None, description="Welcome message")
    order: str | None = Field(None, description="Order info text")
    products: str | None = Field(None, description="Products section header")
    key_name: str | None = Field(None, description="Product key label")
    additional_key_name: str | None = Field(None, description="Additional key label")
    instructions: str | None = Field(None, description="Instructions section header")
    help: str | None = Field(None, description="Help/support text")


class AgreementsNewsletterSignupUpdateRequest(BaseModel):
    subject: str | None = Field(None, description="Email subject line")
    welcome: str | None = Field(None, description="Welcome message")
    confirm_copy: str | None = Field(None, description="Confirmation description text")
    confirm_button: str | None = Field(None, description="Confirmation button label")
    help: str | None = Field(None, description="Help/support text")


# Field length caps:
# - subject + table labels: 256 chars (matches CharField max_length on subject column)
# - intro/closing/header_title/greeting_template: 4096 chars (~600 words; long enough for paragraph copy)
_LABEL_MAX = 256
_COPY_MAX = 4096


class ContactFormsBookingConfirmationUpdateRequest(BaseModel):
    subject: str | None = Field(None, description="Email subject line", max_length=_LABEL_MAX)
    header_title: str | None = Field(None, description="H2 heading at the top of the email", max_length=_COPY_MAX)
    greeting_template: str | None = Field(
        None, description="Greeting line. Use |booker_name| placeholder for booker's name", max_length=_COPY_MAX
    )
    intro_copy: WysiwygStr = Field(None, description="Paragraph rendered above the booking facts", max_length=_COPY_MAX)
    label_datetime: str | None = Field(None, description="Table label for the date & time row", max_length=_LABEL_MAX)
    label_email: str | None = Field(None, description="Table label for the email row", max_length=_LABEL_MAX)
    label_phone: str | None = Field(None, description="Table label for the phone row", max_length=_LABEL_MAX)
    label_company: str | None = Field(None, description="Table label for the company row", max_length=_LABEL_MAX)
    label_message: str | None = Field(None, description="Table label for the message row", max_length=_LABEL_MAX)
    label_video: str | None = Field(
        None, description="Inline label before the video meeting link", max_length=_LABEL_MAX
    )
    closing_copy: WysiwygStr = Field(None, description="Paragraph rendered after the meet link", max_length=_COPY_MAX)


class ContactFormsBookingAdminNotificationUpdateRequest(BaseModel):
    subject: str | None = Field(None, description="Email subject line", max_length=_LABEL_MAX)
    header_title: str | None = Field(None, description="H2 heading", max_length=_COPY_MAX)
    intro_copy: WysiwygStr = Field(None, description="Paragraph rendered above the booking facts", max_length=_COPY_MAX)
    label_datetime: str | None = Field(None, description="Table label for the date & time row", max_length=_LABEL_MAX)
    label_name: str | None = Field(None, description="Table label for the name row", max_length=_LABEL_MAX)
    label_email: str | None = Field(None, description="Table label for the email row", max_length=_LABEL_MAX)
    label_phone: str | None = Field(None, description="Table label for the phone row", max_length=_LABEL_MAX)
    label_company: str | None = Field(None, description="Table label for the company row", max_length=_LABEL_MAX)
    label_message: str | None = Field(None, description="Table label for the message row", max_length=_LABEL_MAX)
    label_video: str | None = Field(
        None, description="Inline label before the video meeting link", max_length=_LABEL_MAX
    )
    closing_copy: WysiwygStr = Field(None, description="Paragraph rendered after the meet link", max_length=_COPY_MAX)


class ContactFormsSubmissionUpdateRequest(BaseModel):
    subject: str | None = Field(None, description="Email subject line", max_length=_LABEL_MAX)
    header_title: str | None = Field(None, description="H2 heading", max_length=_COPY_MAX)
    intro_copy: WysiwygStr = Field(
        None, description="Paragraph rendered above the submission facts", max_length=_COPY_MAX
    )
    label_email: str | None = Field(None, description="Table label for the email row", max_length=_LABEL_MAX)
    label_type: str | None = Field(None, description="Table label for the type row", max_length=_LABEL_MAX)
    label_form: str | None = Field(None, description="Table label for the form row", max_length=_LABEL_MAX)
    label_code: str | None = Field(None, description="Table label for the code row", max_length=_LABEL_MAX)
    label_body: str | None = Field(None, description="Table label for the body row", max_length=_LABEL_MAX)
    closing_copy: WysiwygStr = Field(None, description="Paragraph rendered after the body", max_length=_COPY_MAX)
