# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Submission emails render one table row per submitted field.

django-contact-forms hands over ``form_body_rows``; older versions send only the
pre-formatted ``form_body`` block, which the templates must still render.
"""

from dataclasses import dataclass

import pytest
from django.template.loader import get_template

TEMPLATES = [
    "django_contact_forms/email/contact_form_submission.html",
    "django_contact_forms/email/contact_form_client_copy.html",
]


@dataclass
class Row:
    label: str
    value: str


@pytest.mark.parametrize("template_path", TEMPLATES)
def test_each_row_becomes_its_own_table_row(template_path):
    rows = [Row(label="Full name", value="Ada Lovelace"), Row(label="Message", value="First line\nSecond line")]

    html = get_template(template_path).render({"form_body_rows": rows})

    assert "Full name" in html
    assert "Ada Lovelace" in html
    assert "Message" in html
    # linebreaksbr keeps multi-line answers readable instead of collapsing them
    assert "First line<br>Second line" in html


@pytest.mark.parametrize("template_path", TEMPLATES)
def test_without_rows_the_plain_body_block_still_renders(template_path):
    # An older django-contact-forms sends form_body only; the fallback must survive.
    html = get_template(template_path).render({"form_body": "Whole submission as text"})

    assert "Whole submission as text" in html


@pytest.mark.parametrize("template_path", TEMPLATES)
def test_no_body_at_all_renders_neither_block(template_path):
    html = get_template(template_path).render({})

    assert "Whole submission as text" not in html
    assert "Ada Lovelace" not in html
