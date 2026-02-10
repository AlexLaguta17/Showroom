from django.shortcuts import get_object_or_404

from car_showrooms.models import CarShowroom


class CarShowroomContextMixin:
    @property
    def showroom(self):
        if not hasattr(self, "_showroom"):
            self._showroom = get_object_or_404(
                CarShowroom, pk=self.kwargs["showroom_pk"]
            )
        return self._showroom
