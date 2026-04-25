from fastapi import APIRouter, Depends
from starlette import status
from src.exchanges.dependencies import get_use_case, delete_use_case


router = APIRouter(tags=['Actions with users who have shares'])

@router.get("/user/{username}", status_code=status.HTTP_200_OK)
async def get_user(username: str, get_case: GetUserUseCase = Depends(get_use_case)):
    return await get_case.get_user_by_name(username=username)


@router.delete("/user/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def get_user(username: str, delete_case: DeleteUserUseCase = Depends(delete_use_case)):
    return await delete_case.delete_user_by_name(username=username)