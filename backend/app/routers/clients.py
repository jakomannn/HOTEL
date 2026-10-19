from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_manager, require_manager_with_audit
from app.database.session import get_db
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.services.client_service import (
    create_client,
    delete_client,
    get_client_by_id,
    get_clients,
    update_client,
)


router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
)


@router.post(
    "/",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_client_endpoint(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await create_client(db, client_data)


@router.get(
    "/",
    response_model=list[ClientResponse]
)
async def get_clients_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager)
):
    return await get_clients(db, skip, limit)


@router.get(
    "/{client_id}",
    response_model=ClientResponse
)
async def get_client_endpoint(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager)
):
    return await get_client_by_id(db, client_id)


@router.patch(
    "/{client_id}",
    response_model=ClientResponse
)
async def update_client_endpoint(
    client_id: int,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await update_client(db, client_id, client_data)


@router.delete(
    "/{client_id}",
    response_model=ClientResponse
)
async def delete_client_endpoint(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await delete_client(db, client_id)