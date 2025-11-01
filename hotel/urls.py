from django.contrib import admin
from django.urls import path

from booking import views as booking_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("rooms/create", booking_views.create_room, name="create_room"),
    path(
        "rooms/delete/<int:room_id>",
        booking_views.delete_room,
        name="delete_room",
    ),
    path("rooms/list", booking_views.list_rooms, name="list_rooms"),
    path(
        "bookings/create", booking_views.create_booking, name="create_booking"
    ),
    path(
        "bookings/delete/<int:booking_id>",
        booking_views.delete_booking,
        name="delete_booking",
    ),
    path("bookings/list", booking_views.list_bookings, name="list_bookings"),
]
