# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.template.loader import get_template

from django_email import settings


class EmailTemplate:
    class TemplateList:
        # ACCOUNTS
        NEW_ACCOUNT = settings.NEW_ACCOUNT_EMAIL_TEMPLATE_PATH
        RESET_PASSWORD = settings.RESET_PASSWORD_EMAIL_TEMPLATE_PATH

        # LOYALTY
        COUPON_CONFIRMATION = settings.COUPON_CONFIRMATION_EMAIL_TEMPLATE_PATH

        # RETURNS
        RETURN_CONFIRMATION = settings.RETURN_CONFIRMATION_EMAIL_TEMPLATE_PATH

        # CHECKOUT
        VIRTUAL_PRODUCT = settings.VIRTUAL_PRODUCT_EMAIL_TEMPLATE_PATH
        CHECKOUT_INVOICE = settings.CHECKOUT_INVOICE_EMAIL_TEMPLATE_PATH
        VOUCHER_ISSUED_ON_PURCHASE = settings.VOUCHER_ISSUED_ON_PURCHASE_EMAIL_TEMPLATE_PATH
        VOUCHER_ISSUED_BY_ADMIN = settings.VOUCHER_ISSUED_BY_ADMIN_EMAIL_TEMPLATE_PATH
        VOUCHER_RESEND = settings.VOUCHER_RESEND_EMAIL_TEMPLATE_PATH

        # ALLEGRO
        ALLEGRO_VIRTUAL_PRODUCT = settings.ALLEGRO_VIRTUAL_PRODUCT_EMAIL_TEMPLATE_PATH

        # AGREEMENTS
        NEWSLETTER_SIGNUP = settings.NEWSLETTER_SIGNUP_EMAIL_TEMPLATE_PATH

        # CONTACT_FORMS
        BOOKING_CONFIRMATION = settings.BOOKING_CONFIRMATION_EMAIL_TEMPLATE_PATH
        BOOKING_ADMIN_NOTIFICATION = settings.BOOKING_ADMIN_NOTIFICATION_EMAIL_TEMPLATE_PATH
        CONTACT_FORM_SUBMISSION = settings.CONTACT_FORM_SUBMISSION_EMAIL_TEMPLATE_PATH
        CONTACT_FORM_CLIENT_COPY = settings.CONTACT_FORM_CLIENT_COPY_EMAIL_TEMPLATE_PATH

    class TemplateType:
        HTML = "html"
        TXT = "txt"

    template: str
    context: dict

    def __init__(self, template: str, context: dict = None):
        self.template = template
        self.context = context or {}

    def render_txt(self):
        template = get_template(f"{self.template}.{self.TemplateType.TXT}")
        return template.render(self.context)

    def render_html(self):
        template = get_template(f"{self.template}.{self.TemplateType.HTML}")
        return template.render(self.context)

    def render(self):
        return self.render_txt(), self.render_html()
