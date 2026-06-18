from urllib.parse import urlencode

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings, get_settings, reload_settings, update_env_file
from .image_generation import ComfyUIImageGenerationService, ImageGenerationServiceError
from .schemas import (
    CopywritingRequest,
    CopywritingResponse,
    GeneratedImageFile,
    ImageGenerationRequest,
    ImageGenerationStatusResponse,
    ImageGenerationTaskResponse,
    ModelSettingsRead,
    ModelSettingsWrite,
    ProviderErrorResponse,
    PublishImagePromptRequest,
    PublishImagePromptResponse,
    SeoKeywordRequest,
    SeoKeywordResponse,
)
from .services import GenerationService, GenerationServiceError

_MASKED = "********"


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
        s = get_settings()
        if s.model_provider == "bailian":
            model = s.qwen_model
        elif s.model_provider == "ollama":
            model = s.ollama_model
        else:
            model = s.local_model_name
        return {"status": "ok", "model": model, "provider": s.model_provider}

    @app.get("/api/model-settings", response_model=ModelSettingsRead)
    async def get_model_settings() -> ModelSettingsRead:
        s = get_settings()
        raw_key = s.qwen_api_key.get_secret_value() if s.qwen_api_key else ""
        masked_key = _MASKED if raw_key else ""
        return ModelSettingsRead(
            provider=s.model_provider,
            local_model_base_url=s.local_model_base_url,
            local_model_name=s.local_model_name,
            ollama_base_url=s.ollama_base_url,
            ollama_model=s.ollama_model,
            qwen_api_key=masked_key,
            qwen_base_url=s.qwen_base_url,
            qwen_model=s.qwen_model,
        )

    @app.put("/api/model-settings", response_model=ModelSettingsRead)
    async def put_model_settings(payload: ModelSettingsWrite) -> ModelSettingsRead:
        updates: dict[str, str] = {"MODEL_PROVIDER": payload.provider}

        if payload.local_model_base_url is not None:
            updates["LOCAL_MODEL_BASE_URL"] = payload.local_model_base_url
        if payload.local_model_name is not None:
            updates["LOCAL_MODEL_NAME"] = payload.local_model_name
        if payload.ollama_base_url is not None:
            updates["OLLAMA_BASE_URL"] = payload.ollama_base_url
        if payload.ollama_model is not None:
            updates["OLLAMA_MODEL"] = payload.ollama_model
        if payload.qwen_base_url is not None:
            updates["QWEN_BASE_URL"] = payload.qwen_base_url
        if payload.qwen_model is not None:
            updates["QWEN_MODEL"] = payload.qwen_model
        # 仅在非占位符时才更新 API Key
        if payload.qwen_api_key is not None and payload.qwen_api_key != _MASKED:
            updates["QWEN_API_KEY"] = payload.qwen_api_key

        try:
            update_env_file(updates)
        except OSError as exc:
            raise HTTPException(status_code=500, detail=f"写入配置文件失败：{exc}") from exc

        s = reload_settings()
        raw_key = s.qwen_api_key.get_secret_value() if s.qwen_api_key else ""
        masked_key = _MASKED if raw_key else ""
        return ModelSettingsRead(
            provider=s.model_provider,
            local_model_base_url=s.local_model_base_url,
            local_model_name=s.local_model_name,
            ollama_base_url=s.ollama_base_url,
            ollama_model=s.ollama_model,
            qwen_api_key=masked_key,
            qwen_base_url=s.qwen_base_url,
            qwen_model=s.qwen_model,
        )

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

    @app.post(
        "/api/image-generation/prompts",
        response_model=PublishImagePromptResponse,
        responses={502: {"model": ProviderErrorResponse}},
    )
    async def publish_image_prompts(
        payload: PublishImagePromptRequest,
        service: GenerationService = Depends(get_generation_service),
    ) -> PublishImagePromptResponse:
        try:
            return await service.generate_publish_image_prompts(payload)
        except GenerationServiceError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.post(
        "/api/image-generation/tasks",
        response_model=ImageGenerationTaskResponse,
        responses={502: {"model": ProviderErrorResponse}},
    )
    async def create_image_generation_task(
        payload: ImageGenerationRequest,
        service: ComfyUIImageGenerationService = Depends(get_image_generation_service),
    ) -> ImageGenerationTaskResponse:
        try:
            return await service.submit_task(payload)
        except ImageGenerationServiceError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.get(
        "/api/image-generation/tasks/{prompt_id}",
        response_model=ImageGenerationStatusResponse,
        responses={502: {"model": ProviderErrorResponse}},
    )
    async def get_image_generation_task_status(
        prompt_id: str,
        request: Request,
        service: ComfyUIImageGenerationService = Depends(get_image_generation_service),
    ) -> ImageGenerationStatusResponse:
        try:
            result = await service.get_task_status(prompt_id)
        except ImageGenerationServiceError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        if result.image:
            result.image.url = build_generated_image_url(request, result.image)
        return result

    @app.get(
        "/api/image-generation/view",
        name="view_generated_image",
        responses={502: {"model": ProviderErrorResponse}},
    )
    async def view_generated_image(
        filename: str = Query(...),
        image_type: str = Query("output", alias="type"),
        subfolder: str = Query(""),
        preview: str = Query("WEBP"),
        channel: str = Query("rgb"),
        if_none_match: str | None = Header(default=None, alias="If-None-Match"),
        service: ComfyUIImageGenerationService = Depends(get_image_generation_service),
    ) -> Response:
        try:
            image = await service.read_image(
                filename=filename,
                image_type=image_type,
                subfolder=subfolder,
                preview=preview,
                channel=channel,
            )
        except ImageGenerationServiceError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        headers = build_generated_image_cache_headers(
            etag=image.etag,
            max_age_seconds=service.cache_max_age_seconds,
            cache_hit=image.cache_hit,
        )
        if is_matching_etag(if_none_match, image.etag):
            return Response(status_code=304, headers=headers)

        return Response(content=image.content, media_type=image.media_type, headers=headers)

    return app


def get_generation_service(settings: Settings = Depends(get_settings)) -> GenerationService:
    return GenerationService(settings)


def get_image_generation_service(
    settings: Settings = Depends(get_settings),
) -> ComfyUIImageGenerationService:
    return ComfyUIImageGenerationService(settings)


def build_generated_image_url(request: Request, image: GeneratedImageFile) -> str:
    query = urlencode(
        {
            "filename": image.filename,
            "type": image.type,
            "subfolder": image.subfolder,
            "preview": "WEBP",
            "channel": "rgb",
        }
    )
    return f"{request.url_for('view_generated_image')}?{query}"


def build_generated_image_cache_headers(
    *,
    etag: str,
    max_age_seconds: int,
    cache_hit: bool,
) -> dict[str, str]:
    return {
        "Cache-Control": f"public, max-age={max_age_seconds}, immutable",
        "ETag": etag,
        "X-MDT-Image-Cache": "hit" if cache_hit else "miss",
    }


def is_matching_etag(if_none_match: str | None, etag: str) -> bool:
    if not if_none_match:
        return False
    if if_none_match.strip() == "*":
        return True
    return etag in {candidate.strip() for candidate in if_none_match.split(",")}


app = create_app()
