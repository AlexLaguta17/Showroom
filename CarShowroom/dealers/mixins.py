from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from services.choices import UserType
from dealers.models import Provider, ProviderOrder
from dealers.serializers import ProviderOrderSerializer
from dealers.permissions import IsProviderOrShowroomOwner


class ProviderContextMixin:
    @property
    def provider(self):
        if not hasattr(self, "_provider"):
            self._provider = get_object_or_404(Provider, pk=self.kwargs["provider_pk"])
        return self._provider


class BaseProviderOrderMixin(ProviderContextMixin):
    serializer_class = ProviderOrderSerializer
    permission_classes = (IsAuthenticated, IsProviderOrShowroomOwner)

    def get_queryset(self):
        queryset = ProviderOrder.objects.filter(provider_id=self.provider.id)

        if self.request.user.type == UserType.SHOWROOM:
            showroom_id = self.request.user.carshowroom.id
            queryset = queryset.filter(showroom_id=showroom_id)

        return queryset
