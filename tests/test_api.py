import pytest
from django.test import Client
from django.urls import reverse

STATUS_CODE = 200
LEN_DATA = 2


@pytest.mark.django_db
class TestRooms:
    def test_create_and_list_rooms(self) -> None:
        client = Client()
        # Create rooms
        resp = client.post(
            reverse("create_room"),
            data={"description": "Std", "price": 2000},
            content_type="application/json",
        )
        assert resp.status_code == STATUS_CODE
        room_id1 = resp.json()["room_id"]
        assert room_id1 > 0

        resp = client.post(
            reverse("create_room"),
            data={"description": "Lux", "price": 3000},
            content_type="application/json",
        )
        assert resp.status_code == STATUS_CODE

        # List rooms sorted by price desc
        resp = client.get(
            reverse("list_rooms"), {"sort_by": "price", "order": "desc"}
        )
        assert resp.status_code == STATUS_CODE
        data = resp.json()
        assert isinstance(data, list) and len(data) == LEN_DATA
        assert data[0]["price"] >= data[1]["price"]

    def test_delete_room(self) -> None:
        client = Client()
        resp = client.post(
            reverse("create_room"),
            data={"description": "ToDelete", "price": 1000},
            content_type="application/json",
        )
        room_id = resp.json()["room_id"]
        resp = client.delete(reverse("delete_room", args=[room_id]))
        assert resp.status_code == STATUS_CODE
        assert resp.json()["success"] is True


@pytest.mark.django_db
class TestBookings:
    def setup_method(self) -> None:
        self.client = Client()
        r = self.client.post(
            reverse("create_room"),
            data={"description": "Room", "price": 1500},
            content_type="application/json",
        )
        self.room_id = r.json()["room_id"]

    def test_create_and_list_bookings(self) -> None:
        resp = self.client.post(
            reverse("create_booking"),
            data={
                "room_id": self.room_id,
                "date_start": "2024-12-01",
                "date_end": "2024-12-05",
            },
            content_type="application/json",
        )
        assert resp.status_code == STATUS_CODE
        booking_id = resp.json()["booking_id"]
        assert booking_id > 0

        resp = self.client.get(
            reverse("list_bookings"), {"room_id": self.room_id}
        )
        assert resp.status_code == STATUS_CODE
        data = resp.json()
        assert len(data) == 1
        assert data[0]["date_start"] == "2024-12-01"

    def test_booking_overlap_rejected(self) -> None:
        # First booking
        self.client.post(
            reverse("create_booking"),
            data={
                "room_id": self.room_id,
                "date_start": "2024-06-20",
                "date_end": "2024-06-25",
            },
            content_type="application/json",
        )
        # Overlapping booking
        resp = self.client.post(
            reverse("create_booking"),
            data={
                "room_id": self.room_id,
                "date_start": "2024-06-23",
                "date_end": "2024-06-27",
            },
            content_type="application/json",
        )
        assert resp.status_code in (400, 409)
        assert "error" in resp.json()

    def test_delete_booking(self) -> None:
        resp = self.client.post(
            reverse("create_booking"),
            data={
                "room_id": self.room_id,
                "date_start": "2024-07-01",
                "date_end": "2024-07-02",
            },
            content_type="application/json",
        )
        booking_id = resp.json()["booking_id"]
        resp = self.client.delete(reverse("delete_booking", args=[booking_id]))
        assert resp.status_code == STATUS_CODE
        assert resp.json()["success"] is True
