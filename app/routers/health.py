"""HTTP-маршруты проверки состояния приложения."""

from fastapi import APIRouter, HTTPException, status

from ..services import health_service

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/live")
async def health_live():
    """Проверяет, отвечает ли процесс приложения."""

    return {"status": "alive"}


@router.get(
    "/ready",
    responses={
        503: {
            "description": "Service is not ready",
        }
    },
)
async def health_ready():
    """Проверяет готовность приложения и PostgreSQL."""

    database_ready = (
        await health_service.check_database_ready()
    )

    if not database_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not ready",
        )

    return {"status": "ready"}
