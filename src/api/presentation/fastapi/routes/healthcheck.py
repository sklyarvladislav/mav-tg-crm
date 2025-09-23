from fastapi import APIRouter

router = APIRouter()


@router.get("/healtcheck", tags=["Healtcheck"])
async def healtcheck():
    return {200: "success"}
