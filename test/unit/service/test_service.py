from datetime import date, datetime, time, timedelta, timezone
from freezegun import freeze_time
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
from unittest.mock import ANY
import pytest
from app.service.service import Service


class TestService:
    @pytest.fixture
    def service(self):
        service = Service()
        service.repo = AsyncMock()
        service.jwt = MagicMock()
        return service

    def test_create_token(self, service):
        service.jwt.create_token.return_value = "token"
        result = service.create_token("admin")
        assert result.jwt == "token"
        service.jwt.create_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_room(self, monkeypatch, service):
        monkeypatch.setattr("app.mappers.room.to_bd", lambda x: MagicMock())
        monkeypatch.setattr("app.mappers.room.to_out", lambda x: "room")

        service.repo.create_room.return_value = MagicMock()
        result = await service.create_room(ANY)
        service.repo.create_room.assert_awaited_once()
        assert result == "room"

    @pytest.mark.parametrize(
        "page, page_size, count_room",
        [
            (1, 2, None),
            (1, 4, 100),
        ],
    )
    @pytest.mark.asyncio
    async def test_list_rooms(self, service, page, monkeypatch, page_size, count_room):
        service.repo.get_rooms_count.return_value = count_room
        service.repo.list_rooms_paginated.return_value = MagicMock()

        monkeypatch.setattr("app.mappers.room.list_to_out", lambda x: ["list"])

        result = await service.list_rooms(page, page_size)

        service.repo.get_rooms_count.assert_awaited_once()
        if count_room is None:
            service.repo.list_rooms_paginated.assert_not_awaited()
            assert result == []
        else:
            expected_offset = (page - 1) * page_size
            service.repo.list_rooms_paginated.assert_awaited_once_with(
                expected_offset, page_size, ANY
            )
            assert result == ["list"]

    @pytest.mark.parametrize(
        "room, schedule, expected_status",
        [
            (MagicMock(), None, None),
            (None, MagicMock(), 404),
            (MagicMock(), MagicMock(), 409),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_schedule(
        self, service, monkeypatch, room, schedule, expected_status
    ):
        service.repo.get_room_by_id.return_value = room
        service.repo.get_schedule_by_room_id.return_value = schedule

        monkeypatch.setattr("app.mappers.schedule.to_bd", lambda x, y: MagicMock())
        monkeypatch.setattr("app.mappers.schedule.to_out", lambda x: "schedule")

        if expected_status:
            with pytest.raises(HTTPException) as exc:
                await service.create_schedule("room-id", MagicMock())
            assert exc.value.status_code == expected_status
        else:
            result = await service.create_schedule("room-id", MagicMock())
            assert result == "schedule"

        service.repo.get_room_by_id.assert_awaited_once()
        if room is None:
            service.repo.get_schedule_by_room_id.assert_not_awaited()
            service.repo.create_schedule.assert_not_awaited()
        elif schedule is not None:
            service.repo.get_schedule_by_room_id.assert_awaited_once()
            service.repo.create_schedule.assert_not_awaited()
        else:
            service.repo.get_schedule_by_room_id.assert_awaited_once()
            service.repo.create_schedule.assert_awaited_once()

    @pytest.mark.parametrize(
        "schedule, days, check, test_date, expected_status, expected_path",
        [
            # нет schedule
            (None, None, None, date(2026, 3, 24), None, "empty"),
            # нет в расписание
            (MagicMock(), [1, 3], None, date(2026, 3, 24), None, "empty"),
            # дата в прошлом
            (MagicMock(), [1, 2, 3, 4, 5, 6, 7], None, date(2020, 1, 1), 400, None),
            # создаём слоты
            (
                MagicMock(),
                [1, 2, 3, 4, 5, 6, 7],
                False,
                date(2026, 3, 24),
                None,
                "create",
            ),
            # получаем слоты
            (
                MagicMock(),
                [1, 2, 3, 4, 5, 6, 7],
                True,
                date(2026, 3, 24),
                None,
                "existing",
            ),
        ],
    )
    @freeze_time("2026-03-24")
    @pytest.mark.asyncio
    async def test_list_slots(
        self,
        service,
        monkeypatch,
        schedule,
        days,
        check,
        test_date,
        expected_status,
        expected_path,
    ):
        service.repo.get_schedule_by_room_id.return_value = schedule
        service.repo.exists_slots_in_range.return_value = check
        service.repo.create_slots.return_value = [MagicMock()]
        service.repo.list_available_slots.return_value = [MagicMock()]

        if schedule:
            schedule.days_of_week = days
            schedule.start_time = time(10, 0)
            schedule.end_time = time(11, 0)

        monkeypatch.setattr("app.mappers.slot.to_bd", lambda x, y, z: MagicMock())
        monkeypatch.setattr("app.mappers.slot.list_to_out", lambda x: ["list"])

        if expected_status:
            with pytest.raises(HTTPException) as exc:
                await service.list_slots("room-id", test_date)
            assert exc.value.status_code == expected_status
            return

        result = await service.list_slots("room-id", test_date)

        service.repo.get_schedule_by_room_id.assert_awaited_once()
        if expected_path == "empty":
            service.repo.exists_slots_in_range.assert_not_awaited()
            service.repo.create_slots.assert_not_awaited()
            service.repo.list_available_slots.assert_not_awaited()
            assert result == []

        elif expected_path == "create":
            service.repo.exists_slots_in_range.assert_awaited_once()
            service.repo.create_slots.assert_awaited_once()
            service.repo.list_available_slots.assert_not_awaited()
            assert result == ["list"]

        elif expected_path == "existing":
            service.repo.exists_slots_in_range.assert_awaited_once()
            service.repo.create_slots.assert_not_awaited()
            service.repo.list_available_slots.assert_awaited_once()
            assert result == ["list"]

    @pytest.mark.parametrize(
        "slot, booking, slot_in_past, expected_status, expected_action",
        [
            # нет слота
            (None, None, False, 404, None),
            # срок прошёл слота
            (MagicMock(), None, True, 400, None),
            # забронирован
            (MagicMock(), MagicMock(status="active"), False, 409, None),
            # обновлена отменённая бронь
            (MagicMock(), MagicMock(status="cancel"), False, None, "reactivate"),
            # создана бронь
            (MagicMock(), None, False, None, "create"),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_booking(
        self,
        service,
        monkeypatch,
        slot,
        booking,
        slot_in_past,
        expected_status,
        expected_action,
    ):
        service.repo.get_slot_by_id.return_value = slot
        service.repo.get_booking_by_slot_id.return_value = booking
        service.repo.create_booking.return_value = MagicMock()

        user = MagicMock()
        user.uuid = "user-id"

        request = MagicMock()
        request.slotId = "slot-id"
        request.conferenceLink = True

        if slot:
            slot.end = (
                datetime.now(timezone.utc) - timedelta(days=1)
                if slot_in_past
                else datetime.now(timezone.utc) + timedelta(days=1)
            )

        monkeypatch.setattr("app.mappers.booking.to_bd", lambda x, y, z: MagicMock())
        monkeypatch.setattr("app.mappers.booking.to_out", lambda x: "booking")

        if expected_status:
            with pytest.raises(HTTPException) as exc:
                await service.create_booking(user, request)
            assert exc.value.status_code == expected_status
            return

        result = await service.create_booking(user, request)
        assert result == "booking"

        service.repo.get_slot_by_id.assert_awaited_once()
        service.repo.get_booking_by_slot_id.assert_awaited_once()
        if expected_action == "create":
            service.repo.create_booking.assert_awaited_once()
        elif expected_action == "reactivate":
            service.repo.create_booking.assert_awaited_once()

    @pytest.mark.parametrize(
        "page, page_size, count_room",
        [
            (1, 2, None),
            (1, 4, 100),
        ],
    )
    @pytest.mark.asyncio
    async def test_list_bookings(
        self, service, page, monkeypatch, page_size, count_room
    ):
        service.repo.get_bookings_count.return_value = count_room
        service.repo.list_bookings_paginated.return_value = MagicMock()

        monkeypatch.setattr("app.mappers.booking.list_to_out", lambda x: ["list"])

        result = await service.list_bookings(page, page_size)

        service.repo.get_bookings_count.assert_awaited_once()
        if count_room is None:
            service.repo.list_bookings_paginated.assert_not_awaited()
            assert result == []
        else:
            expected_offset = (page - 1) * page_size
            service.repo.list_bookings_paginated.assert_awaited_once_with(
                expected_offset, page_size, ANY
            )
            assert result == ["list"]

    @pytest.mark.asyncio
    async def test_read_my_bookings(self, service, monkeypatch):
        service.repo.list_user_bookings = AsyncMock(return_value=[MagicMock()])

        user = MagicMock()
        user.uuid = "user-id"

        monkeypatch.setattr(
            "app.mappers.booking.list_to_out",
            lambda x: ["list"],
        )
        result = await service.read_my_bookings(user)
        service.repo.list_user_bookings.assert_awaited_once()
        assert result == ["list"]

    @pytest.mark.parametrize(
        "booking_db, slot, slot_in_past, expected_status",
        [
            # booking не найден
            (None, None, False, 404),
            # чужая бронь
            (MagicMock(user_id="other"), None, False, 403),
            # слот не найден
            (MagicMock(user_id="user-id"), None, False, 500),
            # слот в прошлом
            (MagicMock(user_id="user-id"), MagicMock(), True, 403),
            # успех
            (MagicMock(user_id="user-id"), MagicMock(), False, None),
        ],
    )
    @pytest.mark.asyncio
    async def test_cancel_booking(
        self,
        service,
        booking_db,
        slot,
        slot_in_past,
        expected_status,
    ):
        service.repo.read_booking_by_id.return_value = booking_db
        service.repo.get_slot_by_id.return_value = slot
        service.repo.update_booking.return_value = MagicMock()

        user = MagicMock()
        user.uuid = "user-id"

        if booking_db:
            booking_db.slot_id = "slot-id"

        if slot:
            slot.end = (
                datetime.now(timezone.utc) - timedelta(days=1)
                if slot_in_past
                else datetime.now(timezone.utc) + timedelta(days=1)
            )

        if expected_status:
            with pytest.raises(HTTPException) as exc:
                await service.cancel_booking(user, "booking-id")
            assert exc.value.status_code == expected_status

            service.repo.read_booking_by_id.assert_awaited_once()
            service.repo.update_booking.assert_not_awaited()
            if booking_db is None or booking_db.user_id != "user-id":
                service.repo.get_slot_by_id.assert_not_awaited()
            else:
                service.repo.get_slot_by_id.assert_awaited_once()
            return

        result = await service.cancel_booking(user, "booking-id")

        service.repo.read_booking_by_id.assert_awaited_once()
        service.repo.get_slot_by_id.assert_awaited_once()
        service.repo.update_booking.assert_awaited_once()

        assert result is None
        assert booking_db.status == "cancel"
