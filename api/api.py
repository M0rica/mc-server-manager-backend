from fastapi import APIRouter
from api import file_loader

router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)

router.include_router(file_loader.router)

fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/")
async def read_items():
    return fake_items_db
