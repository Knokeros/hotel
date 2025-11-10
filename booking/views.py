from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Booking, Room
from .serializers import BookingSerializer, RoomSerializer


def handle_exception(error: Exception) -> Response:
    """Универсальный обработчик исключений"""
    if isinstance(error, ValidationError):
        return Response(
            {"error": error.message_dict}, status=status.HTTP_400_BAD_REQUEST
        )
    else:
        # Логируем полную ошибку для разработчиков
        # Но пользователю показываем общее сообщение
        print(f"Server error: {error}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ROOM ENDPOINTS
@api_view(["POST"])
def create_room(request: Request) -> Response:
    serializer = RoomSerializer(data=request.data)
    if serializer.is_valid():
        try:
            room = serializer.save()
            return Response(
                {"room_id": room.id}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return handle_exception(e)
    return Response(
        {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["DELETE"])
def delete_room(request: Request, room_id: int) -> Response:
    if not isinstance(room_id, int):
        return Response(
            {"error": "Invalid room_id type"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    room = Room.objects.filter(id=room_id).first()
    if not room:
        return Response(
            {"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND
        )
    room.delete()
    return Response({"success": True}, status=status.HTTP_200_OK)


@api_view(["GET"])
def list_rooms(request: Request) -> Response:
    try:
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
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return handle_exception(e)


# BOOKING ENDPOINTS
@api_view(["POST"])
def create_booking(request: Request) -> Response:
    serializer = BookingSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        booking = serializer.save()
        return Response(
            {"booking_id": booking.id}, status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e)


@api_view(["DELETE"])
def delete_booking(request: Request, booking_id: int) -> Response:
    try:
        booking = Booking.objects.filter(id=booking_id).first()
        if not booking:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        booking.delete()
        return Response({"success": True}, status=status.HTTP_200_OK)
    except Exception as e:
        return handle_exception(e)


@api_view(["GET"])
def list_bookings(request: Request) -> Response:
    try:
        room_id = request.GET.get("room_id")
        if not room_id:
            return Response(
                {"error": "room_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Валидация room_id
        try:
            room_id_int = int(room_id)
        except (TypeError, ValueError):
            return Response(
                {"error": "room_id must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = Booking.objects.filter(room_id=room_id_int).order_by("date_start")
        serializer = BookingSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return handle_exception(e)
