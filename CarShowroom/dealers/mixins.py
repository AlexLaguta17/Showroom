from django.shortcuts import get_object_or_404

from dealers.models import Provider


class ProviderContextMixin:
    @property
    def provider(self):
        if not hasattr(self, "_provider"):
            self._provider = get_object_or_404(Provider, pk=self.kwargs["provider_pk"])
        return self._provider
