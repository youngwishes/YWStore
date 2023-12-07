from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import Depends
from src.apps.company.service import CompanyService
from src.apps.company.repository import CompanyRepository
from src.core.sql.database import get_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def _company_repository(
    session: AsyncSession = Depends(get_session),
) -> CompanyRepository:
    yield CompanyRepository(session=session)


async def company_service(
    repository: CompanyRepository = Depends(_company_repository),
) -> CompanyService:
    yield CompanyService(repo=repository)


__all__ = ["company_service"]
