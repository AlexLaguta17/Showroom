"""Mixins for the car_showrooms app views."""

from django.shortcuts import get_object_or_404

from car_showrooms.models import CarShowroom


class CarShowroomContextMixin:
    """Resolve and cache the CarShowroom instance from the URL keyword argument."""

    @property
    def showroom(self):
        """Return the CarShowroom identified by ``showroom_pk`` in the URL kwargs."""
        if not hasattr(self, "_showroom"):
            self._showroom = get_object_or_404(CarShowroom, pk=self.kwargs["showroom_pk"])
        return self._showroom
