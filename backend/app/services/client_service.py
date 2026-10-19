from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


async def get_client_by_id(
    db: AsyncSession,
    client_id: int
) -> Client:
    result = await db.execute(
        select(Client).where(Client.client_id == client_id)
    )

    client = result.scalar_one_or_none()

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    return client


async def get_clients(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Client]:
    result = await db.execute(
        select(Client)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_client_by_email(
    db: AsyncSession,
    email: str
) -> Client | None:
    result = await db.execute(
        select(Client).where(Client.email == email)
    )

    return result.scalar_one_or_none()


async def get_client_by_phone(
    db: AsyncSession,
    phone: str
) -> Client | None:
    result = await db.execute(
        select(Client).where(Client.phone == phone)
    )

    return result.scalar_one_or_none()


async def get_or_create_client(
    db: AsyncSession,
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    passport_number: str
) -> Client:
    existing_email_client = await get_client_by_email(db, email)
    existing_phone_client = await get_client_by_phone(db, phone)

    if (
        existing_email_client is not None
        and existing_phone_client is not None
        and existing_email_client.client_id != existing_phone_client.client_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and phone belong to different clients"
        )

    existing_client = existing_email_client or existing_phone_client

    if existing_client is not None:
        return existing_client

    client = Client(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        passport_number=passport_number
    )

    db.add(client)
    await db.flush()

    return client


async def create_client(
    db: AsyncSession,
    client_data: ClientCreate
) -> Client:
    existing_email = await get_client_by_email(db, client_data.email)

    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this email already exists"
        )

    existing_phone = await get_client_by_phone(db, client_data.phone)

    if existing_phone is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this phone already exists"
        )

    client = Client(
        **client_data.model_dump()
    )

    db.add(client)

    try:
        await db.commit()
        await db.refresh(client)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client data violates database constraints"
        )

    return client


async def update_client(
    db: AsyncSession,
    client_id: int,
    client_data: ClientUpdate
) -> Client:
    client = await get_client_by_id(db, client_id)

    update_data = client_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing_email = await get_client_by_email(db, update_data["email"])

        if (
            existing_email is not None
            and existing_email.client_id != client_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this email already exists"
            )

    if "phone" in update_data:
        existing_phone = await get_client_by_phone(db, update_data["phone"])

        if (
            existing_phone is not None
            and existing_phone.client_id != client_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this phone already exists"
            )

    for field, value in update_data.items():
        setattr(client, field, value)

    try:
        await db.commit()
        await db.refresh(client)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client data violates database constraints"
        )

    return client


async def delete_client(
    db: AsyncSession,
    client_id: int
) -> Client:
    client = await get_client_by_id(db, client_id)

    try:
        await db.delete(client)
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client cannot be deleted because it has related records"
        )

    return client