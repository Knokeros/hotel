from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Booking, Room
from .serializers import BookingSerializer, RoomSerializer


# ROOM ENDPOINTS
@api_view(["POST"])
def create_room(request):
    serializer = RoomSerializer(data=request.data)
    if serializer.is_valid():
        room = serializer.save()
        return Response({"room_id": room.id})
    return Response(
        {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["DELETE"])
def delete_room(request, room_id):
    room = Room.objects.filter(id=room_id).first()
    if not room:
        return Response({"error": "Room not found"}, status=404)
    room.delete()
    return Response({"success": True})


@api_view(["GET"])
def list_rooms(request):
    sort_by = request.GET.get("sort_by", "created_at")
    order = request.GET.get("order", "asc")
    allowed_sort = {"price", "created_at"}
    if sort_by not in allowed_sort:
        sort_by = "created_at"
    qs = Room.objects.all()
    if order == "desc":
        sort_by = "-" + sort_by
    qs = qs.order_by(sort_by)
    serializer = RoomSerializer(qs, many=True)
    return Response(serializer.data)


# BOOKING ENDPOINTS
@api_view(["POST"])
def create_booking(request):
    data = request.data.copy()
    try:
        room_id = int(data.get("room_id"))
        date_start = parse_date(data.get("date_start"))
        date_end = parse_date(data.get("date_end"))
        if not (date_start and date_end):
            return Response({"error": "Invalid date format"}, status=400)
        if date_start > date_end:
            return Response(
                {"error": "Start date must not be after end date"}, status=400
            )
        # Check room exists
        room = Room.objects.filter(id=room_id).first()
        if not room:
            return Response({"error": "Room not found"}, status=404)
        # Check booking overlap
        overlap = Booking.objects.filter(
            room_id=room_id, date_start__lte=date_end, date_end__gte=date_start
        ).exists()
        if overlap:
            return Response(
                {"error": "Room already booked for these dates"}, status=409
            )
        booking = Booking.objects.create(
            room=room, date_start=date_start, date_end=date_end
        )
        return Response({"booking_id": booking.id})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["DELETE"])
def delete_booking(request, booking_id):
    booking = Booking.objects.filter(id=booking_id).first()
    if not booking:
        return Response({"error": "Booking not found"}, status=404)
    booking.delete()
    return Response({"success": True})


@api_view(["GET"])
def list_bookings(request):
    room_id = request.GET.get("room_id")
    if not room_id:
        return Response({"error": "room_id is required"}, status=400)
    try:
        qs = Booking.objects.filter(room_id=room_id).order_by("date_start")
        serializer = BookingSerializer(qs, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
