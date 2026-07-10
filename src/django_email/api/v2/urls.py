# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.urls import path

from django_email.api.v2.views import ChannelViewSet, EmailTemplateViewSet, LangChannelConfigViewSet

urlpatterns = [
    # Channels
    path("<str:shop_idx>/channels/", ChannelViewSet.as_view({"get": "list"}), name="email-channel-list"),
    path(
        "<str:shop_idx>/channels/<int:pk>/",
        ChannelViewSet.as_view({"get": "retrieve", "patch": "partial_update"}),
        name="email-channel-detail",
    ),
    # Lang configs (nested under channel)
    path(
        "<str:shop_idx>/channels/<int:channel_pk>/lang-configs/",
        LangChannelConfigViewSet.as_view({"get": "list"}),
        name="email-lang-config-list",
    ),
    # Lang configs (direct access by pk)
    path(
        "<str:shop_idx>/lang-configs/<int:pk>/",
        LangChannelConfigViewSet.as_view({"get": "retrieve", "patch": "partial_update"}),
        name="email-lang-config-detail",
    ),
    # Templates by type
    path(
        "<str:shop_idx>/templates/<slug:email_type>/",
        EmailTemplateViewSet.as_view({"get": "list"}),
        name="email-template-list",
    ),
    path(
        "<str:shop_idx>/templates/<slug:email_type>/<int:pk>/",
        EmailTemplateViewSet.as_view({"get": "retrieve", "patch": "partial_update"}),
        name="email-template-detail",
    ),
]
