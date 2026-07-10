# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models
from django.db.models import QuerySet
from django_utils.api.exceptions import NotFound

from django_email.models import LangChannelConfig


def list_lang_configs(channel_pk: int) -> QuerySet:
    return LangChannelConfig.objects.filter(channel_id=channel_pk).order_by("language")


def get_lang_config(pk: int, shop_idx: str) -> LangChannelConfig:
    try:
        return LangChannelConfig.objects.get(pk=pk, channel__idx=shop_idx)
    except LangChannelConfig.DoesNotExist:
        raise NotFound("Config not found") from None


def update_lang_config(pk: int, shop_idx: str, **fields: object) -> LangChannelConfig:
    config = get_lang_config(pk=pk, shop_idx=shop_idx)
    # Coerce None to "" on non-nullable string columns so the CMS can clear a field
    # by sending null without violating the DB constraint.
    for field, value in fields.items():
        if value is None:
            model_field = LangChannelConfig._meta.get_field(field)
            if not model_field.null and isinstance(model_field, (models.CharField, models.TextField)):
                value = ""
        setattr(config, field, value)
    config.save()
    return config
