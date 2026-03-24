from datetime import date, datetime, time, timedelta, timezone
from freezegun import freeze_time
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
from unittest.mock import ANY
import pytest
from contextlib import nullcontext
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
        def fake_to_out(x):
            return MagicMock()

        def fake_to_bd(x):
            return MagicMock()

        monkeypatch.setattr("app.mappers.room.to_bd", fake_to_bd)
        monkeypatch.setattr("app.mappers.room.to_out", fake_to_out)
        await service.create_room(MagicMock())
        service.repo.create_room.assert_awaited_once_with(ANY, ANY)

    @pytest.mark.parametrize(
        "page, page_size, count_room",
        [
            (1, 2, None),
            (1, 4, 100),
        ],
    )
    @pytest.mark.asyncio
    async def test_list_rooms(self, service, page, page_size, count_room):
        service.repo.get_rooms_count = AsyncMock(return_value=count_room)
        service.repo.list_rooms_paginated = AsyncMock()
        result = await service.list_rooms(page, page_size)
        if count_room is None:
            assert result == []
            service.repo.list_rooms_paginated.assert_not_awaited()
        else:
            expected_offset = (page - 1) * page_size
            service.repo.list_rooms_paginated.assert_awaited_once_with(
                expected_offset, page_size, ANY
            )

    @pytest.mark.parametrize(
        "room, schedule, expec",
        [
            (MagicMock(), None, nullcontext()),
            (None, MagicMock(), pytest.raises(HTTPException)),
            (MagicMock(), MagicMock(), pytest.raises(HTTPException)),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_schedule(self, service, monkeypatch, room, schedule, expec):
        service.repo.get_room_by_id = AsyncMock(return_value=room)
        service.repo.get_schedule_by_room_id = AsyncMock(return_value=schedule)

        def fake_to_bd(x, y):
            return MagicMock()

        def fake_to_out(x):
            return MagicMock()

        monkeypatch.setattr("app.mappers.schedule.to_bd", fake_to_bd)
        monkeypatch.setattr("app.mappers.schedule.to_out", fake_to_out)

        with expec:
            await service.create_schedule("room-id", MagicMock())

    @pytest.mark.parametrize(
        "schedule_exists, days_of_week, check, test_date, expect_exception, expected_result_type",
        [
            (None, None, None, date(2026, 3, 24), False, "empty"),
            (MagicMock(), [], None, date(2026, 3, 24), False, "empty"),
            (
                MagicMock(),
                [date.today().isoweekday()],
                None,
                date(2020, 1, 1),
                False,
                [],
            ),
            (
                MagicMock(),
                [date.today().isoweekday()],
                None,
                date(2026, 3, 24),
                False,
                "create",
            ),
            (
                MagicMock(),
                [date.today().isoweekday()],
                True,
                date(2026, 3, 24),
                False,
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
        schedule_exists,
        days_of_week,
        check,
        test_date,
        expect_exception,
        expected_result_type,
    ):
        service.repo.get_schedule_by_room_id = AsyncMock(return_value=schedule_exists)

        if schedule_exists:
            schedule_exists.days_of_week = list(days_of_week)
            schedule_exists.start_time = time(10, 0)
            schedule_exists.end_time = time(11, 0)

        service.repo.exists_slots_in_range = AsyncMock(return_value=check)

        if expected_result_type == "create":
            service.repo.create_slots = AsyncMock(return_value=[MagicMock()])
        elif expected_result_type == "existing":
            service.repo.list_available_slots = AsyncMock(return_value=[MagicMock()])

        monkeypatch.setattr("app.mappers.slot.to_bd", lambda *args: MagicMock())
        monkeypatch.setattr("app.mappers.slot.list_to_out", lambda x: [])

        if expect_exception:
            with pytest.raises(HTTPException):
                await service.list_slots("room-id", test_date)
        else:
            result = await service.list_slots("room-id", test_date)
            assert isinstance(result, list)

    @pytest.mark.parametrize(
        "slot, booking_exists, booking_status, slot_in_past, expect_exception, action",
        [
            (None, None, None, False, True, None),
            (MagicMock(), None, None, True, True, None),
            (MagicMock(), MagicMock(), "active", False, True, None),
            (MagicMock(), MagicMock(), "cancel", False, False, "reactivate"),
            (MagicMock(), None, None, False, False, "create"),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_booking(
        self,
        service,
        monkeypatch,
        slot,
        booking_exists,
        booking_status,
        slot_in_past,
        expect_exception,
        action,
    ):
        service.repo.get_slot_by_id = AsyncMock(return_value=slot)
        service.repo.get_booking_by_slot_id = AsyncMock(return_value=booking_exists)

        user = MagicMock()
        user.uuid = "user-id"

        booking = MagicMock()
        booking.slotId = "slot-id"
        booking.conferenceLink = True

        if slot:
            slot.end = (
                datetime.now(timezone.utc) - timedelta(days=1)
                if slot_in_past
                else datetime.now(timezone.utc) + timedelta(days=1)
            )

        if booking_exists:
            booking_exists.status = booking_status

        monkeypatch.setattr("app.mappers.booking.to_bd", lambda b, u, l: MagicMock())
        monkeypatch.setattr("app.mappers.booking.to_out", lambda x: MagicMock())

        if action == "reactivate":
            service.repo.create_booking = AsyncMock(return_value=MagicMock())
        elif action == "create":
            service.repo.create_booking = AsyncMock(return_value=MagicMock())

        if expect_exception:
            with pytest.raises(HTTPException):
                await service.create_booking(user, booking)
        else:
            result = await service.create_booking(user, booking)
            assert result is not None

            service.repo.create_booking.assert_awaited_once()

    @pytest.mark.parametrize(
        "total, page, page_size, expected_offset, should_call_list",
        [
            (None, 1, 10, None, False),
            (100, 2, 10, 10, True),
            (0, 1, 10, 0, True),
        ],
    )
    @pytest.mark.asyncio
    async def test_list_bookings(
        self,
        service,
        monkeypatch,
        total,
        page,
        page_size,
        expected_offset,
        should_call_list,
    ):
        service.repo.get_bookings_count = AsyncMock(return_value=total)
        service.repo.list_bookings_paginated = AsyncMock(return_value=[MagicMock()])

        monkeypatch.setattr(
            "app.mappers.booking.list_to_out",
            lambda x: ["mapped"],
        )

        result = await service.list_bookings(page, page_size)

        if total is None:
            assert result == []
            service.repo.list_bookings_paginated.assert_not_awaited()
        else:
            assert result == ["mapped"]

            service.repo.list_bookings_paginated.assert_awaited_once_with(
                expected_offset,
                page_size,
                ANY,
            )

    @pytest.mark.asyncio
    async def test_read_my_bookings(self, service, monkeypatch):
        user = MagicMock()
        user.uuid = "user-id"
        repo_result = [MagicMock()]
        service.repo.list_user_bookings = AsyncMock(return_value=repo_result)
        monkeypatch.setattr(
            "app.mappers.booking.list_to_out",
            lambda x: ["mapped"],
        )
        result = await service.read_my_bookings(user)

        assert result == ["mapped"]

        service.repo.list_user_bookings.assert_awaited_once()

        args, _ = service.repo.list_user_bookings.call_args
        time_arg = args[0]
        user_arg = args[1]

        assert isinstance(time_arg, datetime)
        assert time_arg.tzinfo == timezone.utc
        assert user_arg == user.uuid

    @pytest.mark.parametrize(
        "booking_db, slot, slot_in_past, expect_exception, expected_status",
        [
            (None, None, False, True, 404),
            (MagicMock(user_id="other"), None, False, True, 403),
            (MagicMock(user_id="user-id"), None, False, True, 500),
            (MagicMock(user_id="user-id"), MagicMock(), True, True, 403),
            (MagicMock(user_id="user-id"), MagicMock(), False, False, None),
        ],
    )
    @pytest.mark.asyncio
    async def test_cancel_booking(
        self,
        service,
        booking_db,
        slot,
        slot_in_past,
        expect_exception,
        expected_status,
    ):
        user = MagicMock()
        user.uuid = "user-id"

        service.repo.read_booking_by_id = AsyncMock(return_value=booking_db)

        if booking_db:
            booking_db.slot_id = "slot-id"

        service.repo.get_slot_by_id = AsyncMock(return_value=slot)

        if slot:
            slot.end = (
                datetime.now(timezone.utc) - timedelta(days=1)
                if slot_in_past
                else datetime.now(timezone.utc) + timedelta(days=1)
            )

        service.repo.update_booking = AsyncMock()

        if expect_exception:
            with pytest.raises(HTTPException) as exc:
                await service.cancel_booking(user, "booking-id")

            assert exc.value.status_code == expected_status
        else:
            result = await service.cancel_booking(user, "booking-id")

            assert result is None
            service.repo.update_booking.assert_awaited_once()

            assert booking_db.status == "cancel"
