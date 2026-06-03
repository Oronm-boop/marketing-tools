from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings, get_settings
from .schemas import (
    CopywritingRequest,
    CopywritingResponse,
    ProviderErrorResponse,
    SeoKeywordRequest,
    SeoKeywordResponse,
)
from .services import GenerationService, GenerationServiceError


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="MDT AI Marketing Backend",
        version="0.1.0",
        description="FastAPI backend for SEO keyword and copywriting generation with Qwen.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "model": settings.local_model_name, "provider": "local"}

    @app.post(
        "/api/seo-keywords",
        response_model=SeoKeywordResponse,
        responses={502: {"model": ProviderErrorResponse}},
    )
    async def seo_keywords(
        payload: SeoKeywordRequest,
        service: GenerationService = Depends(get_generation_service),
    ) -> SeoKeywordResponse:
        try:
            return await service.generate_seo_keywords(payload)
        except GenerationServiceError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.post(
        "/api/copywriting",
        response_model=CopywritingResponse,
        responses={502: {"model": ProviderErrorResponse}},
    )
    async def copywriting(
        payload: CopywritingRequest,
        service: GenerationService = Depends(get_generation_service),
    ) -> CopywritingResponse:
        try:
            return await service.generate_copywriting(payload)
        except GenerationServiceError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    return app


def get_generation_service(settings: Settings = Depends(get_settings)) -> GenerationService:
    return GenerationService(settings)


app = create_app()
