from fastapi import APIRouter

router = APIRouter()


@router.get("/healtcheck", tags=["Healtcheck"])
async def healtcheck() -> dict:
    return {200: "success"}
