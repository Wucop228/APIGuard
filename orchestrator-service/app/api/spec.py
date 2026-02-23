from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.spec.schemas import (
    SpecUploadRequest,
    SpecStatusResponse,
    SpecDetailResponse,
    SpecResultResponse,
    AgentCallbackRequest,
)
from app.spec.service import SpecService, SpecServiceError

router = APIRouter(prefix="/spec", tags=["spec"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_spec(
    body: SpecUploadRequest,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = SpecService(session)

    try:
        spec = await service.upload(user_id=user_id, raw_content=body.content)
    except SpecServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {
        "message": "Спецификация загружена и отправлена на обработку",
        "spec_id": spec.id,
        "status": spec.status,
    }


@router.get("/{spec_id}/status", response_model=SpecStatusResponse)
async def get_spec_status(
    spec_id: str,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = SpecService(session)

    try:
        spec = await service.get_status(spec_id=spec_id, user_id=user_id)
    except SpecServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return SpecStatusResponse(
        id=spec.id,
        status=spec.status,
        error_message=spec.error_message,
    )


@router.get("/{spec_id}/results", response_model=SpecDetailResponse)
async def get_spec_results(
    spec_id: str,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = SpecService(session)

    try:
        spec = await service.get_results(spec_id=spec_id, user_id=user_id)
    except SpecServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return SpecDetailResponse(
        id=spec.id,
        status=spec.status,
        parsed_data=spec.parsed_data,
        results=[
            SpecResultResponse(agent_type=r.agent_type, content=r.content)
            for r in spec.results
        ],
        error_message=spec.error_message,
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_my_specs(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = SpecService(session)
    specs = await service.get_user_specs(user_id=user_id)

    return [
        SpecStatusResponse(
            id=s.id,
            status=s.status,
            error_message=s.error_message,
        )
        for s in specs
    ]

@router.post("/{spec_id}/callback", status_code=status.HTTP_200_OK)
async def agent_callback(
    spec_id: str,
    body: AgentCallbackRequest,
    session: AsyncSession = Depends(get_db),
):
    service = SpecService(session)

    try:
        await service.handle_callback(
            spec_id=spec_id,
            agent_type=body.agent_type,
            status=body.status,
            content=body.content,
            error=body.error,
        )
    except SpecServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return {"message": "ok"}