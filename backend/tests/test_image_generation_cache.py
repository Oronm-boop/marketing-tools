import asyncio

from app.config import Settings
from app.image_generation import ComfyUIImageGenerationService


class CountingImageService(ComfyUIImageGenerationService):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.fetch_count = 0

    async def _fetch_image_from_comfyui(self, params: dict[str, str]) -> tuple[bytes, str]:
        self.fetch_count += 1
        return b"cached-image", "image/webp"


def test_generated_image_is_cached_on_disk(tmp_path):
    async def scenario() -> None:
        service = CountingImageService(
            Settings(
                generated_image_cache_dir=tmp_path,
                generated_image_cache_max_age_seconds=60,
            )
        )

        first = await service.read_image(
            filename="MDTMarketing_00001_.png",
            image_type="output",
            subfolder="",
            preview="WEBP",
            channel="rgb",
        )
        second = await service.read_image(
            filename="MDTMarketing_00001_.png",
            image_type="output",
            subfolder="",
            preview="WEBP",
            channel="rgb",
        )

        assert service.fetch_count == 1
        assert first.cache_hit is False
        assert second.cache_hit is True
        assert second.content == b"cached-image"
        assert second.media_type == "image/webp"
        assert second.etag == first.etag
        assert list(tmp_path.glob("*.bin"))

    asyncio.run(scenario())
