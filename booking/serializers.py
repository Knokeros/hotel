from rest_framework import serializers

from .models import Booking, Room


class RoomSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Room
        fields = ["id", "description", "price", "created_at"]


class BookingSerializer(serializers.ModelSerializer):
    date_start = serializers.DateField(format="%Y-%m-%d")
    date_end = serializers.DateField(format="%Y-%m-%d")
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), source="room", write_only=True
    )

    class Meta:
        model = Booking
        fields = ["id", "room_id", "date_start", "date_end"]
