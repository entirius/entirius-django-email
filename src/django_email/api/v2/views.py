# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Any

from django_utils.api.exceptions import NotFound
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from pydantic import ValidationError
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_email.api.v2.errors import raise_pydantic_as_drf
from django_email.api.v2.pagination import AdminPageNumberPagination
from django_email.api.v2.permissions import IsAdminUser
from django_email.schemas.requests.channel import ChannelUpdateRequest
from django_email.schemas.requests.lang_channel_config import LangChannelConfigUpdateRequest
from django_email.schemas.requests.templates import (
    AccountsNewAccountUpdateRequest,
    AccountsResetPasswordUpdateRequest,
    AgreementsNewsletterSignupUpdateRequest,
    AllegroVirtualProductUpdateRequest,
    CheckoutVirtualProductUpdateRequest,
    ContactFormsBookingAdminNotificationUpdateRequest,
    ContactFormsBookingConfirmationUpdateRequest,
    ContactFormsSubmissionUpdateRequest,
    LoyaltyCouponConfirmationUpdateRequest,
    ReturnsReturnConfirmationUpdateRequest,
)
from django_email.schemas.responses.channel import ChannelListResponse, ChannelResponse
from django_email.schemas.responses.lang_channel_config import LangChannelConfigListResponse, LangChannelConfigResponse
from django_email.schemas.responses.templates import (
    AccountsNewAccountResponse,
    AccountsResetPasswordResponse,
    AgreementsNewsletterSignupResponse,
    AllegroVirtualProductResponse,
    CheckoutVirtualProductResponse,
    ContactFormsBookingAdminNotificationResponse,
    ContactFormsBookingConfirmationResponse,
    ContactFormsSubmissionResponse,
    LoyaltyCouponConfirmationResponse,
    ReturnsReturnConfirmationResponse,
    TemplateListResponse,
)
from django_email.services import channel_service, lang_config_service, template_service

EMAIL_TYPE_RESPONSE_SCHEMAS: dict[str, type] = {
    "accounts-new-account": AccountsNewAccountResponse,
    "accounts-reset-password": AccountsResetPasswordResponse,
    "checkout-virtual-product": CheckoutVirtualProductResponse,
    "loyalty-coupon-confirmation": LoyaltyCouponConfirmationResponse,
    "returns-return-confirmation": ReturnsReturnConfirmationResponse,
    "allegro-virtual-product": AllegroVirtualProductResponse,
    "agreements-newsletter-signup": AgreementsNewsletterSignupResponse,
    "contact-forms-booking-confirmation": ContactFormsBookingConfirmationResponse,
    "contact-forms-booking-admin-notification": ContactFormsBookingAdminNotificationResponse,
    "contact-forms-submission": ContactFormsSubmissionResponse,
}

EMAIL_TYPE_UPDATE_SCHEMAS: dict[str, type] = {
    "accounts-new-account": AccountsNewAccountUpdateRequest,
    "accounts-reset-password": AccountsResetPasswordUpdateRequest,
    "checkout-virtual-product": CheckoutVirtualProductUpdateRequest,
    "loyalty-coupon-confirmation": LoyaltyCouponConfirmationUpdateRequest,
    "returns-return-confirmation": ReturnsReturnConfirmationUpdateRequest,
    "allegro-virtual-product": AllegroVirtualProductUpdateRequest,
    "agreements-newsletter-signup": AgreementsNewsletterSignupUpdateRequest,
    "contact-forms-booking-confirmation": ContactFormsBookingConfirmationUpdateRequest,
    "contact-forms-booking-admin-notification": ContactFormsBookingAdminNotificationUpdateRequest,
    "contact-forms-submission": ContactFormsSubmissionUpdateRequest,
}


def _build_channel_response(channel: Any) -> ChannelResponse:
    return ChannelResponse(
        pk=channel.pk,
        idx=channel.idx,
        label=channel.label,
        from_name=channel.from_name,
        from_email=channel.from_email,
        from_t9n=channel.from_t9n,
        main_background_color=channel.main_background_color,
        body_background_color=channel.body_background_color,
        main_text_color=channel.main_text_color,
        brand_text_color=channel.brand_text_color,
        font_family=channel.font_family,
        logo_max_width=channel.logo_max_width,
    )


def _build_lang_config_response(config: Any) -> LangChannelConfigResponse:
    return LangChannelConfigResponse.model_validate(config)


def _build_template_response(instance: object, email_type: str) -> dict:
    schema_class = EMAIL_TYPE_RESPONSE_SCHEMAS[email_type]
    data = schema_class.model_validate(instance).model_dump()
    # Add language_code from the FK relation for CMS display
    lang = getattr(instance, "language", None)
    data["language_code"] = lang.iso2.upper() if lang else None
    return data


@extend_schema_view(
    list=extend_schema(tags=["Email Channels"]),
    retrieve=extend_schema(tags=["Email Channels"]),
    partial_update=extend_schema(tags=["Email Channels"]),
)
class ChannelViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="List email channels",
        description="Returns paginated list of email channels.",
        parameters=[
            OpenApiParameter(
                name="shop_idx", location=OpenApiParameter.PATH, required=True, type=str, description="Shop identifier"
            ),
            OpenApiParameter(
                name="page", location=OpenApiParameter.QUERY, required=False, type=int, description="Page number"
            ),
            OpenApiParameter(
                name="page_size",
                location=OpenApiParameter.QUERY,
                required=False,
                type=int,
                description="Items per page (max 100)",
            ),
        ],
        responses={200: ChannelListResponse},
    )
    def list(self, request: Request, shop_idx: str) -> Response:
        qs = channel_service.list_channels(shop_idx=shop_idx)
        paginator = AdminPageNumberPagination()
        paginated = paginator.paginate_queryset(qs, request)
        response_data = ChannelListResponse(
            count=qs.count(),
            next=paginator.get_next_link(),
            previous=paginator.get_previous_link(),
            results=[_build_channel_response(ch) for ch in paginated],
        )
        return Response(response_data.model_dump(), status=status.HTTP_200_OK)

    @extend_schema(
        summary="Retrieve email channel",
        description="Returns a single email channel by ID.",
        parameters=[
            OpenApiParameter(
                name="shop_idx", location=OpenApiParameter.PATH, required=True, type=str, description="Shop identifier"
            ),
            OpenApiParameter(
                name="pk", location=OpenApiParameter.PATH, required=True, type=int, description="Channel primary key"
            ),
        ],
        responses={200: ChannelResponse, 404: {"description": "Channel not found"}},
    )
    def retrieve(self, request: Request, shop_idx: str, pk: int) -> Response:
        try:
            channel = channel_service.get_channel(pk=int(pk), shop_idx=shop_idx)
        except NotFound:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_build_channel_response(channel).model_dump(), status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update email channel branding",
        description="Partially update channel branding settings (colors, fonts, sender info).",
        parameters=[
            OpenApiParameter(
                name="shop_idx", location=OpenApiParameter.PATH, required=True, type=str, description="Shop identifier"
            ),
            OpenApiParameter(
                name="pk", location=OpenApiParameter.PATH, required=True, type=int, description="Channel primary key"
            ),
        ],
        request=ChannelUpdateRequest,
        responses={
            200: ChannelResponse,
            400: {"description": "Validation error"},
            404: {"description": "Channel not found"},
        },
    )
    def partial_update(self, request: Request, shop_idx: str, pk: int) -> Response:
        try:
            data = ChannelUpdateRequest(**request.data)
        except ValidationError as exc:
            raise_pydantic_as_drf(exc)
        try:
            channel = channel_service.update_channel(
                pk=int(pk), shop_idx=shop_idx, **data.model_dump(exclude_unset=True)
            )
        except NotFound:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_build_channel_response(channel).model_dump(), status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(tags=["Email Lang Configs"]),
    retrieve=extend_schema(tags=["Email Lang Configs"]),
    partial_update=extend_schema(tags=["Email Lang Configs"]),
)
class LangChannelConfigViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="List language configs for channel",
        description="Returns language-specific configurations for an email channel.",
        parameters=[
            OpenApiParameter(
                name="shop_idx", location=OpenApiParameter.PATH, required=True, type=str, description="Shop identifier"
            ),
            OpenApiParameter(
                name="channel_pk",
                location=OpenApiParameter.PATH,
                required=True,
                type=int,
                description="Channel primary key",
            ),
        ],
        responses={200: LangChannelConfigListResponse},
    )
    def list(self, request: Request, shop_idx: str, channel_pk: int) -> Response:
        qs = lang_config_service.list_lang_configs(channel_pk=int(channel_pk))
        paginator = AdminPageNumberPagination()
        paginated = paginator.paginate_queryset(qs, request)
        response_data = LangChannelConfigListResponse(
            count=qs.count(),
            next=paginator.get_next_link(),
            previous=paginator.get_previous_link(),
            results=[_build_lang_config_response(c) for c in paginated],
        )
        return Response(response_data.model_dump(), status=status.HTTP_200_OK)

    @extend_schema(
        summary="Retrieve language config",
        description="Returns a single language configuration.",
        parameters=[
            OpenApiParameter(
                name="shop_idx", location=OpenApiParameter.PATH, required=True, type=str, description="Shop identifier"
            ),
            OpenApiParameter(
                name="pk", location=OpenApiParameter.PATH, required=True, type=int, description="Config primary key"
            ),
        ],
        responses={200: LangChannelConfigResponse, 404: {"description": "Config not found"}},
    )
    def retrieve(self, request: Request, shop_idx: str, pk: int) -> Response:
        try:
            config = lang_config_service.get_lang_config(pk=int(pk), shop_idx=shop_idx)
        except NotFound:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_build_lang_config_response(config).model_dump(), status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update language config",
        description="Partially update language-specific configuration (footer, social links, etc.).",
        parameters=[
            OpenApiParameter(
                name="shop_idx", location=OpenApiParameter.PATH, required=True, type=str, description="Shop identifier"
            ),
            OpenApiParameter(
                name="pk", location=OpenApiParameter.PATH, required=True, type=int, description="Config primary key"
            ),
        ],
        request=LangChannelConfigUpdateRequest,
        responses={
            200: LangChannelConfigResponse,
            400: {"description": "Validation error"},
            404: {"description": "Config not found"},
        },
    )
    def partial_update(self, request: Request, shop_idx: str, pk: int) -> Response:
        try:
            data = LangChannelConfigUpdateRequest(**request.data)
        except ValidationError as exc:
            raise_pydantic_as_drf(exc)
        try:
            config = lang_config_service.update_lang_config(
                pk=int(pk), shop_idx=shop_idx, **data.model_dump(exclude_unset=True)
            )
        except NotFound:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_build_lang_config_response(config).model_dump(), status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(tags=["Email Templates"]),
    retrieve=extend_schema(tags=["Email Templates"]),
    partial_update=extend_schema(tags=["Email Templates"]),
)
class EmailTemplateViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="List templates by type",
        description="Returns email templates for a specific type and channel.",
        parameters=[
            OpenApiParameter(
                name="shop_idx",
                location=OpenApiParameter.PATH,
                required=True,
                type=str,
                description="Shop identifier (used as channel idx lookup)",
            ),
            OpenApiParameter(
                name="email_type",
                location=OpenApiParameter.PATH,
                required=True,
                type=str,
                description=(
                    "Email type slug: accounts-new-account, accounts-reset-password, "
                    "checkout-virtual-product, loyalty-coupon-confirmation, "
                    "returns-return-confirmation, allegro-virtual-product, "
                    "agreements-newsletter-signup"
                ),
            ),
        ],
        responses={200: TemplateListResponse, 404: {"description": "Unknown email type"}},
    )
    def list(self, request: Request, shop_idx: str, email_type: str) -> Response:
        try:
            qs = template_service.list_templates(email_type=email_type, shop_idx=shop_idx)
        except NotFound:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        paginator = AdminPageNumberPagination()
        paginated = paginator.paginate_queryset(qs, request)
        results = [_build_template_response(t, email_type) for t in paginated]
        response_data = TemplateListResponse(
            count=qs.count(), next=paginator.get_next_link(), previous=paginator.get_previous_link(), results=results
        )
        return Response(response_data.model_dump(), status=status.HTTP_200_OK)

    @extend_schema(
        summary="Retrieve email template",
        description="Returns a single email template by ID.",
        parameters=[
            OpenApiParameter(
                name="shop_idx", location=OpenApiParameter.PATH, required=True, type=str, description="Shop identifier"
            ),
            OpenApiParameter(
                name="email_type",
                location=OpenApiParameter.PATH,
                required=True,
                type=str,
                description="Email type slug",
            ),
            OpenApiParameter(
                name="pk", location=OpenApiParameter.PATH, required=True, type=int, description="Template primary key"
            ),
        ],
        responses={200: AccountsNewAccountResponse, 404: {"description": "Template not found"}},
    )
    def retrieve(self, request: Request, shop_idx: str, email_type: str, pk: int) -> Response:
        try:
            instance = template_service.get_template(email_type=email_type, pk=int(pk), shop_idx=shop_idx)
        except NotFound:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_build_template_response(instance, email_type), status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update email template",
        description="Partially update email template text content.",
        parameters=[
            OpenApiParameter(
                name="shop_idx", location=OpenApiParameter.PATH, required=True, type=str, description="Shop identifier"
            ),
            OpenApiParameter(
                name="email_type",
                location=OpenApiParameter.PATH,
                required=True,
                type=str,
                description="Email type slug",
            ),
            OpenApiParameter(
                name="pk", location=OpenApiParameter.PATH, required=True, type=int, description="Template primary key"
            ),
        ],
        request=AccountsNewAccountUpdateRequest,
        responses={
            200: AccountsNewAccountResponse,
            400: {"description": "Validation error"},
            404: {"description": "Template not found"},
        },
    )
    def partial_update(self, request: Request, shop_idx: str, email_type: str, pk: int) -> Response:
        update_schema = EMAIL_TYPE_UPDATE_SCHEMAS.get(email_type)
        if not update_schema:
            return Response({"detail": f"Unknown email type: {email_type}"}, status=status.HTTP_404_NOT_FOUND)
        try:
            data = update_schema(**request.data)
        except ValidationError as exc:
            raise_pydantic_as_drf(exc)
        try:
            instance = template_service.update_template(
                email_type=email_type, pk=int(pk), shop_idx=shop_idx, **data.model_dump(exclude_unset=True)
            )
        except NotFound:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_build_template_response(instance, email_type), status=status.HTTP_200_OK)
