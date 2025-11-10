from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models


class Room(models.Model):
    description = models.TextField(validators=[MinLengthValidator(5)])
    price = models.IntegerField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Дополнительная логика валидации
        if "spam" in self.description.lower():
            raise ValidationError("Description contains forbidden words.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Проверка перед сохранением
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Room #{self.id} — {self.price}₽"


class Booking(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    date_start = models.DateField()
    date_end = models.DateField()

    def clean(self):
        if self.date_start > self.date_end:
            raise ValidationError("Start date must not be after end date.")

        # Проверка пересечения броней (только для новых)
        overlap_exists = (
            Booking.objects.filter(
                room=self.room,
                date_start__lte=self.date_end,
                date_end__gte=self.date_start,
            )
            .exclude(id=self.id)
            .exists()
        )

        if overlap_exists:
            raise ValidationError("Room already booked for these dates.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking #{self.id} — Room {self.room_id}"
