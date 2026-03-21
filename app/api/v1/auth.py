from fastapi import APIRouter, status
from typing import Annotated

router = APIRouter(tags=["Auth"])


@router.get("/dummyLogin/", status_code=status.HTTP_200_OK)
async def dummy_login(
    refresh_token: Annotated[str, Cookie(...)],
) -> Token:
    return await AuthGateWay().refresh_token(refresh_token)