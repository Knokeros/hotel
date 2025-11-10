import pytest
from django.test import Client
from django.urls import reverse

STATUS_CODE_CREATED = 201
STATUS_CODE_SUCCESS = 200
STATUS_CODE_BAD_REQUEST = 400
LEN_DATA = 2


@pytest.mark.django_db
class TestRooms:
    def test_create_and_list_rooms(self) -> None:
        client = Client()
        # Create rooms
        resp = client.post(
            reverse("create_room"),
            data={"description": "Standard room with view", "price": 2000},
            content_type="application/json",
        )
        assert resp.status_code == STATUS_CODE_CREATED
        room_id1 = resp.json()["room_id"]
        assert room_id1 > 0

        resp = client.post(
            reverse("create_room"),
            data={"description": "Luxury suite with balcony", "price": 3000},
            content_type="application/json",
        )
        assert resp.status_code == STATUS_CODE_CREATED

        # List rooms sorted by price desc
        resp = client.get(
            reverse("list_rooms"), {"sort_by": "price", "order": "desc"}
        )
        assert resp.status_code == STATUS_CODE_SUCCESS
        data = resp.json()
        assert isinstance(data, list) and len(data) == LEN_DATA
        assert data[0]["price"] >= data[1]["price"]

    def test_create_room_validation_error(self) -> None:
        """Тест на валидацию - короткое описание"""
        client = Client()
        resp = client.post(
            reverse("create_room"),
            data={
                "description": "Bad",
                "price": 2000,
            },  # Слишком короткое описание
            content_type="application/json",
        )
        assert resp.status_code == STATUS_CODE_BAD_REQUEST
        assert "error" in resp.json()

    def test_create_room_spam_validation(self) -> None:
        """Тест на валидацию - запрещенные слова"""
        client = Client()
        resp = client.post(
            reverse("create_room"),
            data={"description": "This is spam content", "price": 2000},
            content_type="application/json",
        )
        assert resp.status_code == STATUS_CODE_BAD_REQUEST
        assert "error" in resp.json()

    def test_create_room_negative_price(self) -> None:
        """Тест на валидацию - отрицательная цена"""
        client = Client()
        resp = client.post(
            reverse("create_room"),
            data={"description": "Nice room", "price": -100},
            content_type="application/json",
        )
        assert resp.status_code == STATUS_CODE_BAD_REQUEST
        assert "error" in resp.json()

    def test_delete_room(self) -> None:
        client = Client()
        resp = client.post(
            reverse("create_room"),
            data={"description": "Room to delete later", "price": 1000},
            content_type="application/json",
        )
        assert resp.status_code == STATUS_CODE_CREATED
        room_id = resp.json()["room_id"]

        resp = client.delete(reverse("delete_room", args=[room_id]))
        assert resp.status_code == STATUS_CODE_SUCCESS
        assert resp.json()["success"] is True

    def test_delete_nonexistent_room(self) -> None:
        client = Client()
        resp = client.delete(reverse("delete_room", args=[99999]))
        assert resp.status_code == 404
        assert "error" in resp.json()


@pytest.mark.django_db
class TestBookings:
    def setup_method(self) -> None:
        self.client = Client()
        # Создаем комнату с корректным описанием
        r = self.client.post(
            reverse("create_room"),
            data={
                "description": "Comfortable room for testing",
                "price": 1500,
            },
            content_type="application/json",
        )
        # Проверяем, что комната создалась успешно
        assert r.status_code == STATUS_CODE_CREATED
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
        assert resp.status_code == STATUS_CODE_CREATED
        booking_id = resp.json()["booking_id"]
        assert booking_id > 0

        resp = self.client.get(
            reverse("list_bookings"), {"room_id": self.room_id}
        )
        assert resp.status_code == STATUS_CODE_SUCCESS
        data = resp.json()
        assert len(data) == 1
        assert data[0]["date_start"] == "2024-12-01"

    def test_booking_overlap_rejected(self) -> None:
        # First booking
        resp1 = self.client.post(
            reverse("create_booking"),
            data={
                "room_id": self.room_id,
                "date_start": "2024-06-20",
                "date_end": "2024-06-25",
            },
            content_type="application/json",
        )
        assert resp1.status_code == STATUS_CODE_CREATED

        # Overlapping booking
        resp2 = self.client.post(
            reverse("create_booking"),
            data={
                "room_id": self.room_id,
                "date_start": "2024-06-23",
                "date_end": "2024-06-27",
            },
            content_type="application/json",
        )
        assert resp2.status_code == STATUS_CODE_BAD_REQUEST
        assert "error" in resp2.json()

    def test_booking_invalid_dates(self) -> None:
        """Тест на некорректные даты (start > end)"""
        resp = self.client.post(
            reverse("create_booking"),
            data={
                "room_id": self.room_id,
                "date_start": "2024-12-10",
                "date_end": "2024-12-05",  # end раньше start
            },
            content_type="application/json",
        )
        assert resp.status_code == STATUS_CODE_BAD_REQUEST
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
        assert resp.status_code == STATUS_CODE_CREATED
        booking_id = resp.json()["booking_id"]

        resp = self.client.delete(reverse("delete_booking", args=[booking_id]))
        assert resp.status_code == STATUS_CODE_SUCCESS
        assert resp.json()["success"] is True

    def test_delete_nonexistent_booking(self) -> None:
        resp = self.client.delete(reverse("delete_booking", args=[99999]))
        assert resp.status_code == 404
        assert "error" in resp.json()

    def test_list_bookings_without_room_id(self) -> None:
        """Тест на запрос бронирований без room_id"""
        resp = self.client.get(reverse("list_bookings"))
        assert resp.status_code == STATUS_CODE_BAD_REQUEST
        assert "error" in resp.json()

    def test_list_bookings_invalid_room_id(self) -> None:
        """Тест на запрос бронирований с невалидным room_id"""
        resp = self.client.get(
            reverse("list_bookings"), {"room_id": "invalid"}
        )
        assert resp.status_code == STATUS_CODE_BAD_REQUEST
        assert "error" in resp.json()

    def test_list_bookings_nonexistent_room(self) -> None:
        """Тест на запрос бронирований для несуществующей комнаты"""
        resp = self.client.get(reverse("list_bookings"), {"room_id": 99999})
        assert resp.status_code == STATUS_CODE_SUCCESS
        data = resp.json()
        assert data == []  # Должен вернуть пустой список


@pytest.mark.django_db
class TestRoomSorting:
    def test_room_sorting_options(self) -> None:
        client = Client()

        # Создаем несколько комнат
        client.post(
            reverse("create_room"),
            data={"description": "Room A", "price": 3000},
            content_type="application/json",
        )
        client.post(
            reverse("create_room"),
            data={"description": "Room B", "price": 2000},
            content_type="application/json",
        )
        client.post(
            reverse("create_room"),
            data={"description": "Room C", "price": 4000},
            content_type="application/json",
        )

        # Сортировка по цене по возрастанию
        resp = client.get(
            reverse("list_rooms"), {"sort_by": "price", "order": "asc"}
        )
        assert resp.status_code == STATUS_CODE_SUCCESS
        prices = [room["price"] for room in resp.json()]
        assert prices == sorted(prices)

        # Сортировка по цене по убыванию
        resp = client.get(
            reverse("list_rooms"), {"sort_by": "price", "order": "desc"}
        )
        assert resp.status_code == STATUS_CODE_SUCCESS
        prices = [room["price"] for room in resp.json()]
        assert prices == sorted(prices, reverse=True)

        # Сортировка по дате создания (по умолчанию)
        resp = client.get(reverse("list_rooms"))
        assert resp.status_code == STATUS_CODE_SUCCESS
        data = resp.json()
        assert len(data) == 3

        # Невалидный параметр сортировки
        resp = client.get(reverse("list_rooms"), {"sort_by": "invalid_field"})
        assert (
            resp.status_code == STATUS_CODE_SUCCESS
        )  # Должен использовать значение по умолчанию
