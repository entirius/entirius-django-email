# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db.models import QuerySet
from django_utils.api.exceptions import NotFound

from django_email.models import Channel


def list_channels(shop_idx: str) -> QuerySet:
    return Channel.objects.filter(idx=shop_idx).order_by("idx")


def get_channel_by_idx(shop_idx: str) -> Channel:
    channel = Channel.objects.filter(idx=shop_idx).first()
    if not channel:
        raise NotFound("Channel not found")
    return channel


def get_channel(pk: int, shop_idx: str) -> Channel:
    try:
        return Channel.objects.get(pk=pk, idx=shop_idx)
    except Channel.DoesNotExist:
        raise NotFound("Channel not found")


def update_channel(pk: int, shop_idx: str, **fields: object) -> Channel:
    channel = get_channel(pk=pk, shop_idx=shop_idx)
    for field, value in fields.items():
        setattr(channel, field, value)
    channel.save()
    return channel
