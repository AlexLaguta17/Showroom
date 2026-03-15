"""Mixins for the dealers app views."""

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from services.choices import UserType
from dealers.models import Provider, ProviderOrder
from dealers.serializers import ProviderOrderSerializer
from dealers.permissions import IsProviderOrShowroomOwner


class ProviderContextMixin:
    """Resolve and cache the Provider instance from the URL keyword argument."""

    @property
    def provider(self):
        """Return the Provider identified by ``provider_pk`` in the URL kwargs."""
        if not hasattr(self, "_provider"):
            self._provider = get_object_or_404(Provider, pk=self.kwargs["provider_pk"])
        return self._provider


class BaseProviderOrderMixin(ProviderContextMixin):
    """Base mixin for provider order views: queryset, serializer, and permissions."""

    serializer_class = ProviderOrderSerializer
    permission_classes = (IsAuthenticated, IsProviderOrShowroomOwner)

    def get_queryset(self):
        """Return orders for the current provider, scoped to the requesting showroom if applicable."""
        queryset = ProviderOrder.objects.filter(provider_id=self.provider.id).select_related(
            "provider", "showroom", "car"
        )

        if self.request.user.type == UserType.SHOWROOM:
            if not hasattr(self.request.user, "carshowroom"):
                return queryset.none()
            showroom_id = self.request.user.carshowroom.id
            queryset = queryset.filter(showroom_id=showroom_id)

        return queryset
