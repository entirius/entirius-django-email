# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_email", "0001_squashed_0016_merge_checkoutvoucher_clientcopy"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contactformssubmission",
            name="subject",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Email subject. Put <contact_form_id> in the text to have the submission id "
                    "substituted there — that is what gives every notification its own mail "
                    "thread instead of stacking them in one. Leave the token out and no id is added."
                ),
                max_length=256,
            ),
        ),
    ]
